import io
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APITestCase
from core.models import Subject, Course
from vault.models import Resource

User = get_user_model()

class ResourceVaultCrudTests(APITestCase):
    def setUp(self):
        # Create users
        self.user = User.objects.create_user(
            email='student@example.edu',
            password='StrongPassword123!',
            full_name='Study Linker'
        )
        self.other_user = User.objects.create_user(
            email='other@example.edu',
            password='StrongPassword123!',
            full_name='Other Linker'
        )

        # Create subjects and courses
        self.subject = Subject.objects.create(name='Computer Science', slug='cs')
        self.course = Course.objects.create(
            subject=self.subject,
            name='Intro to Programming',
            code='CS101'
        )
        self.other_subject = Subject.objects.create(name='Mathematics', slug='math')
        self.other_course = Course.objects.create(
            subject=self.other_subject,
            name='Calculus I',
            code='MATH101'
        )

        # URLs
        self.list_create_url = reverse('resource-list-create')

    def test_upload_resource_success(self):
        self.client.force_authenticate(user=self.user)

        pdf_content = b"%PDF-1.4 dummy pdf content"
        uploaded_file = SimpleUploadedFile(
            name="notes.pdf",
            content=pdf_content,
            content_type="application/pdf"
        )

        data = {
            'title': 'CS101 Lecture Notes',
            'file': uploaded_file,
            'subject': self.subject.id,
            'course': self.course.id
        }

        response = self.client.post(self.list_create_url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'CS101 Lecture Notes')
        self.assertEqual(response.data['status'], 'PROCESSING')
        self.assertEqual(response.data['upvote_count'], 0)
        self.assertEqual(response.data['uploader']['email'], self.user.email)

        # Verify row created in db
        self.assertEqual(Resource.objects.count(), 1)
        resource = Resource.objects.first()
        self.assertEqual(resource.title, 'CS101 Lecture Notes')
        self.assertEqual(resource.status, 'PROCESSING')
        self.assertTrue(resource.file_path.name.startswith('notes'))
        self.assertTrue(resource.file_path.name.endswith('.pdf'))

    def test_upload_resource_not_pdf_fails(self):
        self.client.force_authenticate(user=self.user)

        txt_content = b"some dummy text content"
        uploaded_file = SimpleUploadedFile(
            name="notes.txt",
            content=txt_content,
            content_type="text/plain"
        )

        data = {
            'title': 'CS101 Lecture Notes',
            'file': uploaded_file,
            'subject': self.subject.id,
            'course': self.course.id
        }

        response = self.client.post(self.list_create_url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('file', response.data['fields'])
        self.assertEqual(response.data['fields']['file'][0], "Only PDF documents are allowed.")

    def test_upload_resource_course_subject_mismatch_fails(self):
        self.client.force_authenticate(user=self.user)

        pdf_content = b"%PDF-1.4 dummy pdf content"
        uploaded_file = SimpleUploadedFile(
            name="notes.pdf",
            content=pdf_content,
            content_type="application/pdf"
        )

        # MATH101 course does not belong to CS subject
        data = {
            'title': 'Mismatch Notes',
            'file': uploaded_file,
            'subject': self.subject.id,
            'course': self.other_course.id
        }

        response = self.client.post(self.list_create_url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('course', response.data['fields'])
        self.assertEqual(response.data['fields']['course'][0], "The course must belong to the selected subject.")

    def test_upload_resource_unauthenticated_fails(self):
        pdf_content = b"%PDF-1.4 dummy pdf content"
        uploaded_file = SimpleUploadedFile(
            name="notes.pdf",
            content=pdf_content,
            content_type="application/pdf"
        )

        data = {
            'title': 'CS101 Lecture Notes',
            'file': uploaded_file,
            'subject': self.subject.id,
            'course': self.course.id
        }

        response = self.client.post(self.list_create_url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

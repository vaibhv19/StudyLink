from django.test import TestCase
from django.urls import reverse
from django.core.management import call_command
from django.db import transaction, IntegrityError
from rest_framework import status
from rest_framework.test import APITestCase
from core.models import Subject, Course

class TagModelTests(TestCase):
    def test_subject_creation_and_uniqueness(self):
        sub1 = Subject.objects.create(name='Bioengineering', slug='bioengineering')
        self.assertEqual(sub1.name, 'Bioengineering')
        self.assertEqual(sub1.slug, 'bioengineering')
        
        # Test uniqueness of name
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Subject.objects.create(name='Bioengineering', slug='bio-eng')
            
        # Test uniqueness of slug
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Subject.objects.create(name='Other Bio', slug='bioengineering')

    def test_course_creation_and_relationship(self):
        sub = Subject.objects.create(name='Bioengineering', slug='bioengineering')
        course = Course.objects.create(subject=sub, name='Biochemistry', code='BIO101')
        
        self.assertEqual(course.code, 'BIO101')
        self.assertEqual(course.subject, sub)
        self.assertIn(course, sub.courses.all())
        
        # Test uniqueness of code
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Course.objects.create(subject=sub, name='Another Course', code='BIO101')

class TagSeedCommandTests(TestCase):
    def test_seed_tags_idempotent(self):
        # 1. Run seed command first time
        call_command('seed_tags')
        
        subject_count = Subject.objects.count()
        course_count = Course.objects.count()
        
        self.assertTrue(subject_count > 0)
        self.assertTrue(course_count > 0)
        
        # 2. Run seed command again
        call_command('seed_tags')
        
        self.assertEqual(Subject.objects.count(), subject_count)
        self.assertEqual(Course.objects.count(), course_count)

class TagAPITests(APITestCase):
    def setUp(self):
        self.sub_cs = Subject.objects.create(name='Computer Science', slug='computer-science')
        self.sub_math = Subject.objects.create(name='Mathematics', slug='mathematics')
        
        self.c1 = Course.objects.create(subject=self.sub_cs, name='Intro to Programming', code='CS101')
        self.c2 = Course.objects.create(subject=self.sub_cs, name='Data Structures', code='CS102')
        self.c3 = Course.objects.create(subject=self.sub_math, name='Calculus I', code='MATH101')
        
        self.subjects_url = reverse('core:subject-list')
        self.courses_url = reverse('core:course-list')

    def test_get_subjects_list_public(self):
        response = self.client.get(self.subjects_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verify pagination structure
        self.assertIn('count', response.data)
        self.assertIn('results', response.data)
        
        # CS and Math should be returned sorted by name
        results = response.data['results']
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['name'], 'Computer Science')
        self.assertEqual(results[1]['name'], 'Mathematics')

    def test_get_courses_list_public_with_nesting(self):
        response = self.client.get(self.courses_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        self.assertEqual(len(results), 3)
        
        # Check nested subject details
        first_course = results[0]
        self.assertIn('subject', first_course)
        self.assertEqual(first_course['subject']['slug'], 'computer-science')

    def test_filter_courses_by_subject_slug(self):
        # Filter for CS courses only
        response = self.client.get(self.courses_url, {'subject': 'computer-science'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        self.assertEqual(len(results), 2)
        for item in results:
            self.assertEqual(item['subject']['slug'], 'computer-science')

        # Filter for Math courses only
        response = self.client.get(self.courses_url, {'subject': 'mathematics'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['code'], 'MATH101')

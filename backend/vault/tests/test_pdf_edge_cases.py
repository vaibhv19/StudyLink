import io
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from pypdf import PdfWriter
from core.models import Subject, Course
from vault.models import Resource
from vault.tasks import process_pdf_document_task
from vault.services import PDFIngestionService

User = get_user_model()

def create_clean_text_pdf() -> bytes:
    """Creates a PDF with clean extractable text."""
    writer = PdfWriter()
    page = writer.add_blank_page(width=200, height=200)
    # In pypdf, creating text requires standard page stream or canvas.
    # Alternatively, we can inject text objects into page stream or use standard PDF stream.
    stream = io.BytesIO()
    # Write a minimal valid PDF with text stream
    pdf_bytes = (
        b"%PDF-1.4\n"
        b"1 0 obj <</Type /Catalog /Pages 2 0 R>> endobj\n"
        b"2 0 obj <</Type /Pages /Kids [3 0 R] /Count 1>> endobj\n"
        b"3 0 obj <</Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources <</Font <</F1 5 0 R>>>>>> endobj\n"
        b"4 0 obj <</Length 55>> stream\n"
        b"BT /F1 12 Tf 72 712 Td (Calculus II Series Convergence Notes) Tj ET\n"
        b"endstream endobj\n"
        b"5 0 obj <</Type /Font /Subtype /Type1 /BaseFont /Helvetica>> endobj\n"
        b"xref\n0 6\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000234 00000 n \n0000000339 00000 n \n"
        b"trailer <</Size 6 /Root 1 0 R>>\nstartxref\n418\n%%EOF\n"
    )
    return pdf_bytes

def create_scanned_image_pdf() -> bytes:
    """Creates a PDF containing blank pages without extractable text."""
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    stream = io.BytesIO()
    writer.write(stream)
    return stream.getvalue()

def create_password_protected_pdf(password="StudyLinkSecurePass123") -> bytes:
    """Creates an encrypted/password-protected PDF."""
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    writer.encrypt(password)
    stream = io.BytesIO()
    writer.write(stream)
    return stream.getvalue()


class PDFEdgeCaseTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='student_pdf@example.edu',
            password='StrongPassword123!',
            full_name='PDF Tester'
        )
        self.subject = Subject.objects.create(name='Mathematics', slug='math')
        self.course = Course.objects.create(name='Calculus II', code='MATH201', subject=self.subject)

    @patch('rag.client.GeminiClient.get_embedding')
    def test_clean_text_pdf_ingestion_success(self, mock_embedding):
        """
        Verify that a clean text PDF extracts text chunks, queries embeddings,
        and transitions the Resource status to READY.
        """
        mock_embedding.return_value = [0.123] * 768

        pdf_content = create_clean_text_pdf()
        file_obj = SimpleUploadedFile("clean_notes.pdf", pdf_content, content_type="application/pdf")

        resource = Resource.objects.create(
            uploader=self.user,
            subject=self.subject,
            course=self.course,
            title="Clean Lecture Notes",
            file_path=file_obj,
            status="PROCESSING"
        )

        result = process_pdf_document_task(str(resource.id))
        resource.refresh_from_db()

        self.assertEqual(resource.status, 'READY')
        self.assertIn("processed successfully", result)
        self.assertGreater(resource.chunks.count(), 0)

        first_chunk = resource.chunks.first()
        self.assertIn("Calculus II", first_chunk.content)
        self.assertEqual(first_chunk.page_number, 1)

    def test_scanned_image_pdf_becomes_unsearchable(self):
        """
        Verify that a scanned/image-only PDF with no extractable text
        is marked as UNSEARCHABLE without failing or crashing.
        """
        pdf_content = create_scanned_image_pdf()
        file_obj = SimpleUploadedFile("scanned_doc.pdf", pdf_content, content_type="application/pdf")

        resource = Resource.objects.create(
            uploader=self.user,
            subject=self.subject,
            course=self.course,
            title="Scanned Drawing Doc",
            file_path=file_obj,
            status="PROCESSING"
        )

        result = process_pdf_document_task(str(resource.id))
        resource.refresh_from_db()

        self.assertEqual(resource.status, 'UNSEARCHABLE')
        self.assertIn("UNSEARCHABLE", result)
        self.assertEqual(resource.chunks.count(), 0)

    def test_password_protected_pdf_fails_gracefully(self):
        """
        Verify that a password-protected/encrypted PDF is handled gracefully
        and marks the Resource status as FAILED without unhandled crash.
        """
        pdf_content = create_password_protected_pdf("SecretLockedPass")
        file_obj = SimpleUploadedFile("locked_notes.pdf", pdf_content, content_type="application/pdf")

        resource = Resource.objects.create(
            uploader=self.user,
            subject=self.subject,
            course=self.course,
            title="Locked Exam Notes",
            file_path=file_obj,
            status="PROCESSING"
        )

        with self.assertRaises(Exception):
            process_pdf_document_task(str(resource.id))

        resource.refresh_from_db()
        self.assertEqual(resource.status, 'FAILED')
        self.assertEqual(resource.chunks.count(), 0)

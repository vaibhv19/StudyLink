import os
import shutil
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.core.files import File
from django.contrib.auth import get_user_model
from core.models import Subject, Course
from vault.models import Resource
from vault.tasks import process_pdf_document_task

User = get_user_model()

# Map courses to academic subjects
SUBJECT_MAP = {
    'Electronics': ('Electronics Engineering', 'electronics-engineering'),
    'DE': ('Electronics Engineering', 'electronics-engineering'),
    'Maths-2': ('Mathematics', 'mathematics'),
    'M4': ('Mathematics', 'mathematics'),
    'UHVPE': ('Humanities & Social Sciences', 'humanities-social-sciences'),
    'TC': ('Humanities & Social Sciences', 'humanities-social-sciences'),
    'COI': ('Humanities & Social Sciences', 'humanities-social-sciences'),
    # Default maps to ('Computer Science', 'computer-science')
}

# Map course code/abbreviations to Course Name and unique Code
COURSE_MAP = {
    'Electronics': ('Basic Electronics', 'EC101'),
    'Maths-2': ('Mathematics II', 'MATH102'),
    'DE': ('Digital Electronics', 'EC201'),
    'DS': ('Data Structures', 'CS201'),
    'DSTL': ('Discrete Structures & Theory of Logic', 'CS202'),
    'Python': ('Python Programming', 'CS203'),
    'UHVPE': ('Universal Human Values & Professional Ethics', 'HVE101'),
    'CyberSecurity': ('Cyber Security', 'CS301'),
    'M4': ('Mathematics IV', 'MATH202'),
    'OPPs in java': ('Object-Oriented Programming in Java', 'CS204'),
    'OS': ('Operating Systems', 'CS205'),
    'TAFL': ('Theory of Automata and Formal Languages', 'CS206'),
    'TC': ('Technical Communication', 'HUM101'),
    'AI': ('Artificial Intelligence', 'CS302'),
    'CC': ('Cloud Computing', 'CS303'),
    'COI': ('Constitution of India', 'HUM102'),
    'DAA': ('Design and Analysis of Algorithms', 'CS304'),
    'DBMS': ('Database Management Systems', 'CS305'),
    'OOSD': ('Object Oriented System Design', 'CS306'),
    'CN': ('Computer Networks', 'CS401'),
    'DA': ('Data Analytics', 'CS402'),
    'EITK': ('Emerging Technology for Engineering', 'CS403'),
    'SE': ('Software Engineering', 'CS404'),
    'SMADA': ('Social Media Analytics and Data Analysis', 'CS405'),
    'SPM': ('Software Project Management', 'CS406'),
}

class Command(BaseCommand):
    help = 'Recursively scans a local directory to import PDF study materials into StudyLink.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--path',
            type=str,
            default=r"D:\College Study",
            help='Path to the directory containing study materials'
        )

    def handle(self, *args, **options):
        root_path = options['path']
        
        if not os.path.exists(root_path):
            self.stdout.write(self.style.ERROR(f"Specified path does not exist: {root_path}"))
            return

        # 1. Setup Uploader User
        uploader = User.objects.filter(is_superuser=True).first()
        if not uploader:
            uploader = User.objects.first()
        if not uploader:
            uploader = User.objects.create_user(
                email="system_seeder@example.com",
                password="StudyLinkSeederPassword123!",
                full_name="System Seeder"
            )
            self.stdout.write(self.style.SUCCESS(f"Created a system seeder user: {uploader.email}"))
        else:
            self.stdout.write(self.style.SUCCESS(f"Using uploader user: {uploader.email}"))

        self.stdout.write(f"Scanning directory: {root_path}...")
        
        pdf_count = 0
        imported_count = 0
        
        # 2. Walk through the directory structure
        semesters = ["sem 2", "sem 3", "sem 4", "sem 5", "sem 6"]
        
        for sem in semesters:
            sem_dir = os.path.join(root_path, sem)
            if not os.path.exists(sem_dir):
                continue
                
            self.stdout.write(self.style.MIGRATE_HEADING(f"\nProcessing folder: {sem}"))
            
            # Subdirectories under semester represent courses
            course_dirs = [d for d in os.listdir(sem_dir) if os.path.isdir(os.path.join(sem_dir, d))]
            
            for course_abbrev in course_dirs:
                course_path = os.path.join(sem_dir, course_abbrev)
                
                # Determine Subject Name & Slug
                subject_name, subject_slug = SUBJECT_MAP.get(
                    course_abbrev,
                    ('Computer Science', 'computer-science')
                )
                
                # Get or Create Subject
                subject, _ = Subject.objects.get_or_create(
                    name=subject_name,
                    defaults={'slug': subject_slug}
                )
                
                # Determine Course Name & Code
                course_display_name, course_code = COURSE_MAP.get(
                    course_abbrev,
                    (f"{course_abbrev} Course", course_abbrev.upper())
                )
                
                # Get or Create Course
                course, _ = Course.objects.get_or_create(
                    code=course_code,
                    defaults={
                        'name': course_display_name,
                        'subject': subject
                    }
                )
                
                # Scan this course directory for PDFs recursively
                for r, d, files in os.walk(course_path):
                    for filename in files:
                        if filename.lower().endswith('.pdf'):
                            pdf_count += 1
                            local_file_path = os.path.join(r, filename)
                            
                            # Clean up the title from filename
                            title = os.path.splitext(filename)[0].replace('_', ' ').replace('-', ' ').strip()
                            
                            # We can also prepend subfolder context if it is something like Notes, PYQs
                            subfolder = os.path.basename(r)
                            if subfolder.lower() not in [course_abbrev.lower(), 'notes', 'pyqs', 'pyq']:
                                title = f"[{subfolder}] {title}"
                            else:
                                title = f"[{course_abbrev}] {title}"
                                
                            # Check if already imported
                            # We check by title, subject, and course
                            exists = Resource.objects.filter(
                                title=title,
                                subject=subject,
                                course=course
                            ).exists()
                            
                            if exists:
                                self.stdout.write(f"  Skipping (already exists): {title}")
                                continue
                                
                            self.stdout.write(f"  Importing: {title}...")
                            
                            try:
                                with open(local_file_path, 'rb') as f:
                                    resource = Resource.objects.create(
                                        uploader=uploader,
                                        title=title,
                                        subject=subject,
                                        course=course,
                                        status='PROCESSING',
                                        file_path=File(f, name=filename)
                                    )
                                
                                # Call process PDF document task synchronously to chunk and index it
                                self.stdout.write(f"    Running PDF ingestion and RAG index for Resource ID: {resource.id}...")
                                result = process_pdf_document_task(str(resource.id))
                                self.stdout.write(self.style.SUCCESS(f"    Result: {result}"))
                                imported_count += 1
                                
                            except Exception as ex:
                                self.stdout.write(self.style.ERROR(f"    Failed to import/process {filename}: {str(ex)}"))
                                
        self.stdout.write(self.style.SUCCESS(
            f"\nImport process completed! Found {pdf_count} PDF files, successfully imported and indexed {imported_count} new resources."
        ))

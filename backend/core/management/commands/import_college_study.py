import os
import shutil
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.core.files import File
from django.conf import settings
from django.contrib.auth import get_user_model
from core.models import Subject, Course
from vault.models import Resource
from vault.tasks import process_pdf_document_task

User = get_user_model()

# Map semester folder to Subject details
SEMESTER_MAP = {
    'sem 2': ('Semester 2', 'semester-2'),
    'sem 3': ('Semester 3', 'semester-3'),
    'sem 4': ('Semester 4', 'semester-4'),
    'sem 5': ('Semester 5', 'semester-5'),
    'sem 6': ('Semester 6', 'semester-6'),
}

# Map course code/abbreviations to Course Name
COURSE_MAP = {
    'Electronics': 'Basic Electronics',
    'Maths-2': 'Mathematics II',
    'DE': 'Digital Electronics',
    'DS': 'Data Structures',
    'DSTL': 'Discrete Structures & Theory of Logic',
    'Python': 'Python Programming',
    'UHVPE': 'Universal Human Values & Professional Ethics',
    'CyberSecurity': 'Cyber Security',
    'M4': 'Mathematics IV',
    'OPPs in java': 'Object-Oriented Programming in Java',
    'OS': 'Operating Systems',
    'TAFL': 'Theory of Automata and Formal Languages',
    'TC': 'Technical Communication',
    'AI': 'Artificial Intelligence',
    'CC': 'Cloud Computing',
    'COI': 'Constitution of India',
    'DAA': 'Design and Analysis of Algorithms',
    'DBMS': 'Database Management Systems',
    'OOSD': 'Object Oriented System Design',
    'CN': 'Computer Networks',
    'DA': 'Data Analytics',
    'EITK': 'Emerging Technology for Engineering',
    'SE': 'Software Engineering',
    'SMADA': 'Social Media Analytics and Data Analysis',
    'SPM': 'Software Project Management',
}

class Command(BaseCommand):
    help = 'Recursively scans a local directory to import PDF study materials into StudyLink organized by semesters.'

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

        # 1. Clear Database and Media resources
        self.stdout.write("Resetting previous resources, courses, subjects, and media directories...")
        Resource.objects.all().delete()
        Course.objects.all().delete()
        Subject.objects.all().delete()
        
        resources_dir = os.path.join(settings.MEDIA_ROOT, 'resources')
        if os.path.exists(resources_dir):
            try:
                shutil.rmtree(resources_dir)
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Could not delete media resources directory: {e}"))
        os.makedirs(resources_dir, exist_ok=True)
        self.stdout.write(self.style.SUCCESS("Cleanup completed!"))

        # 2. Setup Uploader User
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
        
        # 3. Walk through the directory structure
        semesters = ["sem 2", "sem 3", "sem 4", "sem 5", "sem 6"]
        
        for sem_key in semesters:
            sem_dir = os.path.join(root_path, sem_key)
            if not os.path.exists(sem_dir):
                continue
                
            self.stdout.write(self.style.MIGRATE_HEADING(f"\nProcessing folder: {sem_key}"))
            
            # Get Subject (Semester) details
            subj_name, subj_slug = SEMESTER_MAP.get(sem_key, (sem_key.capitalize(), slugify(sem_key)))
            subject, _ = Subject.objects.get_or_create(
                name=subj_name,
                defaults={'slug': subj_slug}
            )
            
            # Subdirectories under semester represent courses
            course_dirs = [d for d in os.listdir(sem_dir) if os.path.isdir(os.path.join(sem_dir, d))]
            
            for course_abbrev in course_dirs:
                course_path = os.path.join(sem_dir, course_abbrev)
                
                # Determine Course Name & Code
                course_display_name = COURSE_MAP.get(course_abbrev, f"{course_abbrev} Course")
                course_code = course_abbrev.upper()
                
                # Get or Create Course under the Subject (Semester)
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
                            
                            # Prepend subfolder context if it is something like Notes, PYQs
                            subfolder = os.path.basename(r)
                            if subfolder.lower() not in [course_abbrev.lower(), 'notes', 'pyqs', 'pyq']:
                                title = f"[{subfolder}] {title}"
                            else:
                                title = f"[{course_abbrev}] {title}"
                                
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
                                result = process_pdf_document_task(str(resource.id))
                                self.stdout.write(self.style.SUCCESS(f"    Result: {result}"))
                                imported_count += 1
                                
                            except Exception as ex:
                                self.stdout.write(self.style.ERROR(f"    Failed to import/process {filename}: {str(ex)}"))
                                
        self.stdout.write(self.style.SUCCESS(
            f"\nImport process completed! Reset database and successfully imported/indexed {imported_count} new resources under Semester categories."
        ))

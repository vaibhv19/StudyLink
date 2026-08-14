from django.core.management.base import BaseCommand
from django.utils.text import slugify
from core.models import Subject, Course

class Command(BaseCommand):
    help = 'Seeds the database with standard academic subjects and courses'

    def handle(self, *args, **options):
        # Define seed data
        data = {
            'Computer Science': [
                {'code': 'CS101', 'name': 'Intro to Programming'},
                {'code': 'CS102', 'name': 'Data Structures and Algorithms'},
                {'code': 'CS203', 'name': 'Systems Programming'},
            ],
            'Mathematics': [
                {'code': 'MATH101', 'name': 'Calculus I'},
                {'code': 'MATH201', 'name': 'Calculus II'},
                {'code': 'MATH302', 'name': 'Linear Algebra'},
            ],
            'Physics': [
                {'code': 'PHYS101', 'name': 'General Physics I'},
                {'code': 'PHYS102', 'name': 'General Physics II'},
            ],
            'Chemistry': [
                {'code': 'CHEM101', 'name': 'General Chemistry I'},
                {'code': 'CHEM110', 'name': 'Organic Chemistry'},
            ]
        }

        self.stdout.write('Seeding subjects and courses...')

        for subject_name, courses in data.items():
            subject_slug = slugify(subject_name)
            subject, created = Subject.objects.get_or_create(
                name=subject_name,
                defaults={'slug': subject_slug}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created Subject: {subject_name}"))
            else:
                self.stdout.write(f"Subject '{subject_name}' already exists.")

            for course_info in courses:
                course, c_created = Course.objects.get_or_create(
                    code=course_info['code'],
                    defaults={
                        'name': course_info['name'],
                        'subject': subject
                    }
                )
                if c_created:
                    self.stdout.write(self.style.SUCCESS(f"  Created Course: {course_info['code']} - {course_info['name']}"))
                else:
                    # If it exists, let's make sure it's linked to the correct subject and name
                    course.name = course_info['name']
                    course.subject = subject
                    course.save()
                    self.stdout.write(f"  Course '{course_info['code']}' already exists.")

        self.stdout.write(self.style.SUCCESS('Successfully completed database seeding.'))

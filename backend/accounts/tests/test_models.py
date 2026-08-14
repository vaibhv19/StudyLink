from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError

User = get_user_model()

class CustomUserModelTests(TestCase):
    def test_create_user_successful(self):
        user = User.objects.create_user(
            email='STUDENT@example.edu',
            password='securepassword123',
            full_name='Test Student'
        )
        self.assertEqual(user.email, 'STUDENT@example.edu')  # Email normalization can be done, base django normalizes domain name
        self.assertTrue(user.check_password('securepassword123'))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertIsNotNone(user.id)
        self.assertEqual(user.provider, 'local')

    def test_create_user_without_email_raises_error(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(
                email='',
                password='password123',
                full_name='No Email'
            )

    def test_create_user_without_password_for_oauth(self):
        # OAuth users don't have passwords initially
        user = User.objects.create_user(
            email='oauthstudent@example.edu',
            password=None,
            full_name='OAuth Student',
            provider='google',
            linked_google=True
        )
        self.assertFalse(user.has_usable_password())
        self.assertEqual(user.provider, 'google')
        self.assertTrue(user.linked_google)
        self.assertFalse(user.linked_github)

    def test_create_superuser_successful(self):
        superuser = User.objects.create_superuser(
            email='admin@example.edu',
            password='adminpassword123',
            full_name='Admin User'
        )
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.has_usable_password())

    def test_create_superuser_invalid_fields_raises_error(self):
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email='admin@example.edu',
                password='adminpassword123',
                full_name='Admin User',
                is_staff=False
            )
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email='admin@example.edu',
                password='adminpassword123',
                full_name='Admin User',
                is_superuser=False
            )

    def test_email_uniqueness_enforced(self):
        User.objects.create_user(
            email='duplicate@example.edu',
            password='password123',
            full_name='Original'
        )
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                email='duplicate@example.edu',
                password='password456',
                full_name='Duplicate'
            )

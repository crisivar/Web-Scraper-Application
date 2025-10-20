from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from ..forms import CustomUserCreationForm, EmailAuthenticationForm


class AuthenticationFormsTest(TestCase):
    """Test authentication forms"""

    def test_custom_user_creation_form_valid(self):
        """Test user creation form with valid data"""
        form_data = {
            'email': 'newuser@example.com',
            'password1': 'complexpass123',
            'password2': 'complexpass123'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_custom_user_creation_form_duplicate_email(self):
        """Test user creation form rejects duplicate email"""
        User.objects.create_user(
            username='existing@example.com',
            email='existing@example.com',
            password='testpass123'
        )

        form_data = {
            'email': 'existing@example.com',
            'password1': 'complexpass123',
            'password2': 'complexpass123'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_custom_user_creation_form_password_mismatch(self):
        """Test user creation form rejects password mismatch"""
        form_data = {
            'email': 'newuser@example.com',
            'password1': 'complexpass123',
            'password2': 'differentpass123'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_email_authentication_form_valid(self):
        """Test email authentication form field validation"""
        # Create a user to authenticate against
        User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='testpass123'
        )

        form_data = {
            'username': 'test@example.com',
            'password': 'testpass123'
        }

        # Create form with mock request for authentication
        request = RequestFactory().post('/')

        form = EmailAuthenticationForm(request, data=form_data)
        self.assertTrue(form.is_valid())

    def test_email_authentication_form_invalid_email(self):
        """Test email authentication form with invalid email format"""
        form_data = {
            'username': 'invalid-email',
            'password': 'testpass123'
        }
        form = EmailAuthenticationForm(data=form_data)
        self.assertFalse(form.is_valid())

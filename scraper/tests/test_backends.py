from django.test import TestCase
from django.contrib.auth.models import User
from ..backends import EmailBackend


class EmailBackendTest(TestCase):
    """Test custom email authentication backend"""

    def setUp(self):
        self.backend = EmailBackend()
        self.user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='testpass123'
        )

    def test_authenticate_with_email_success(self):
        """Test successful authentication with email"""
        user = self.backend.authenticate(
            None,
            username='test@example.com',
            password='testpass123'
        )
        self.assertEqual(user, self.user)

    def test_authenticate_with_email_wrong_password(self):
        """Test authentication fails with wrong password"""
        user = self.backend.authenticate(
            None,
            username='test@example.com',
            password='wrongpassword'
        )
        self.assertIsNone(user)

    def test_authenticate_with_nonexistent_email(self):
        """Test authentication fails with non-existent email"""
        user = self.backend.authenticate(
            None,
            username='nonexistent@example.com',
            password='testpass123'
        )
        self.assertIsNone(user)

    def test_get_user_success(self):
        """Test getting user by ID"""
        user = self.backend.get_user(self.user.id)
        self.assertEqual(user, self.user)

    def test_get_user_nonexistent(self):
        """Test getting non-existent user returns None"""
        user = self.backend.get_user(99999)
        self.assertIsNone(user)

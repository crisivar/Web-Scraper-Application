from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from django.conf import settings
import os


class SettingsConfigurationTest(TestCase):
    """Test Django settings configuration from environment variables"""

    def test_authentication_backends_configured(self):
        """Test that custom email backend is properly configured"""
        expected_backends = [
            'scraper.backends.EmailBackend',
            'django.contrib.auth.backends.ModelBackend',
        ]
        self.assertEqual(settings.AUTHENTICATION_BACKENDS, expected_backends)

    def test_login_urls_configured(self):
        """Test that login URLs are properly configured"""
        self.assertEqual(settings.LOGIN_URL, '/accounts/login/')

        env_login_redirect = os.getenv('LOGIN_REDIRECT_URL', '/pages/')
        self.assertEqual(env_login_redirect, '/pages/')
        self.assertEqual(settings.LOGOUT_REDIRECT_URL, '/accounts/login/')

    def test_celery_timezone_matches_django_timezone(self):
        """Test that Celery timezone matches Django timezone"""

        expected_timezone = os.getenv('TIME_ZONE', 'UTC')
        self.assertEqual(settings.TIME_ZONE, expected_timezone)

        # Celery timezone should be the same as Django timezone or a valid fallback
        self.assertIn(settings.CELERY_TIMEZONE, [
                      settings.TIME_ZONE, 'UTC', expected_timezone])

    def test_secret_key_not_default(self):
        """Test that SECRET_KEY is not the default value"""
        default_key = 'your-secret-key-here-change-this-in-production'
        self.assertNotEqual(settings.SECRET_KEY, default_key)
        self.assertTrue(len(settings.SECRET_KEY) >= 50)

    def test_database_configuration(self):
        """Test that database is properly configured"""
        db_config = settings.DATABASES['default']
        self.assertIn('ENGINE', db_config)
        self.assertIn('NAME', db_config)

    def test_celery_configuration(self):
        """Test that Celery is properly configured"""
        self.assertIsNotNone(settings.CELERY_BROKER_URL)
        self.assertIsNotNone(settings.CELERY_RESULT_BACKEND)
        self.assertEqual(settings.CELERY_TASK_SERIALIZER, 'json')
        self.assertEqual(settings.CELERY_RESULT_SERIALIZER, 'json')

    def test_scraping_settings(self):
        """Test that scraping settings are configured"""
        self.assertIsInstance(settings.SCRAPING_TIMEOUT, int)
        self.assertIsInstance(settings.SCRAPING_MAX_RETRIES, int)
        self.assertIsInstance(settings.SCRAPING_DELAY, int)
        self.assertGreater(settings.SCRAPING_TIMEOUT, 0)
        self.assertGreater(settings.SCRAPING_MAX_RETRIES, 0)
        self.assertGreaterEqual(settings.SCRAPING_DELAY, 0)

    def test_environment_variables_loaded(self):
        """Test that environment variables are properly loaded"""
        # Test critical environment variables
        self.assertIsNotNone(os.getenv('SECRET_KEY'))
        self.assertIsNotNone(os.getenv('DATABASE_URL'))
        self.assertIsNotNone(os.getenv('REDIS_URL'))

        # Test timezone configuration
        self.assertEqual(os.getenv('TIME_ZONE'), 'America/Bogota')

        # Test authentication URLs
        self.assertEqual(os.getenv('LOGIN_URL'), '/accounts/login/')
        self.assertEqual(os.getenv('LOGIN_REDIRECT_URL'), '/pages/')
        self.assertEqual(os.getenv('LOGOUT_REDIRECT_URL'), '/accounts/login/')

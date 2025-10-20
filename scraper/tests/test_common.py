"""
Common test configurations and fixtures for scraper app tests.

This module contains shared test utilities and configurations
that can be used across multiple test files.
"""

from django.contrib.auth.models import User


class TestDataMixin:
    """Mixin class with common test data creation methods."""

    @classmethod
    def create_test_user(cls, email='test@example.com', password='testpass123'):
        """Create a test user with given email and password."""
        return User.objects.create_user(
            username=email,
            email=email,
            password=password
        )

    @classmethod
    def create_other_user(cls, email='other@example.com', password='testpass123'):
        """Create another test user for isolation tests."""
        return User.objects.create_user(
            username=email,
            email=email,
            password=password
        )


# Common test data
TEST_HTML_WITH_LINKS = '''
<html>
    <head><title>Test Page</title></head>
    <body>
        <a href="https://example.com/page1">Page 1</a>
        <a href="https://example.com/page2">Page 2</a>
        <a href="/relative">Relative Link</a>
        <a href="mailto:test@example.com">Email Link</a>
        <p>Some text without links</p>
    </body>
</html>
'''

TEST_HTML_NO_LINKS = '''
<html>
    <head><title>No Links Page</title></head>
    <body>
        <p>This page has no links</p>
        <div>Just some content</div>
    </body>
</html>
'''

# Test URLs
TEST_URLS = {
    'valid': 'https://example.com',
    'invalid': 'not-a-url',
    'with_path': 'https://example.com/page',
    'with_query': 'https://example.com/page?param=value'
}

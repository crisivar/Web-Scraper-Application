from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.db import IntegrityError
from ..models import ScrapedPage, PageLink


class ScrapedPageModelTest(TestCase):
    """Test ScrapedPage model"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='testpass123'
        )

    def test_scraped_page_creation(self):
        """Test creating a scraped page"""
        page = ScrapedPage.objects.create(
            user=self.user,
            url='https://example.com',
            title='Test Page'
        )
        self.assertEqual(page.status, 'pending')
        self.assertEqual(page.link_count, 0)
        self.assertEqual(str(page), 'Test Page - test@example.com')

    def test_scraped_page_get_absolute_url(self):
        """Test get_absolute_url method"""
        page = ScrapedPage.objects.create(
            user=self.user,
            url='https://example.com',
            title='Test Page'
        )
        expected_url = reverse('scraper:page_detail', kwargs={'pk': page.pk})
        self.assertEqual(page.get_absolute_url(), expected_url)

    def test_scraped_page_unique_together(self):
        """Test unique constraint on user and URL"""
        ScrapedPage.objects.create(
            user=self.user,
            url='https://example.com',
            title='Test Page'
        )

        with self.assertRaises(IntegrityError):
            ScrapedPage.objects.create(
                user=self.user,
                url='https://example.com',
                title='Duplicate Page'
            )

    def test_page_link_creation(self):
        """Test creating page links"""
        page = ScrapedPage.objects.create(
            user=self.user,
            url='https://example.com',
            title='Test Page'
        )
        link = PageLink.objects.create(
            page=page,
            url='https://example.com/link1',
            name='Test Link'
        )
        self.assertEqual(page.link_count, 1)
        self.assertTrue(str(link).startswith('Test Link'))
        self.assertIn('https://example.com/link1', str(link))

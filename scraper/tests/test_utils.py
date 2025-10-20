from django.test import TestCase
from django.contrib.auth.models import User
import responses
from ..models import ScrapedPage
from ..utils import scrape_page_links


class ScrapingUtilsTest(TestCase):
    """Test scraping utilities"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='testpass123'
        )

    @responses.activate
    def test_scrape_page_links_success(self):
        """Test successful page scraping"""
        page = ScrapedPage.objects.create(
            user=self.user,
            url='https://example.com',
            title='Test Page'
        )

        html_content = '''
        <html>
            <body>
                <a href="https://example.com/page1">Page 1</a>
                <a href="https://example.com/page2">Page 2</a>
                <a href="/relative">Relative Link</a>
            </body>
        </html>
        '''

        responses.add(
            responses.GET,
            'https://example.com',
            body=html_content,
            status=200,
            content_type='text/html'
        )

        # Call the scraping function
        scrape_page_links(page)

        # Refresh from database
        page.refresh_from_db()

        self.assertEqual(page.status, 'completed')
        self.assertEqual(page.links.count(), 3)

        # Check that links were created
        links = list(page.links.values('url', 'name'))
        self.assertIn({'url': 'https://example.com/page1',
                      'name': 'Page 1'}, links)
        self.assertIn({'url': 'https://example.com/page2',
                      'name': 'Page 2'}, links)
        self.assertIn({'url': 'https://example.com/relative',
                      'name': 'Relative Link'}, links)

    @responses.activate
    def test_scrape_page_links_empty_page(self):
        """Test scraping page with no links"""
        page = ScrapedPage.objects.create(
            user=self.user,
            url='https://example.com',
            title='Test Page'
        )

        html_content = '<html><body><p>No links here</p></body></html>'

        responses.add(
            responses.GET,
            'https://example.com',
            body=html_content,
            status=200,
            content_type='text/html'
        )

        scrape_page_links(page)

        page.refresh_from_db()
        self.assertEqual(page.status, 'completed')
        self.assertEqual(page.links.count(), 0)

    @responses.activate
    def test_scrape_page_links_network_error(self):
        """Test scraping with network error"""
        page = ScrapedPage.objects.create(
            user=self.user,
            url='https://example.com',
            title='Test Page'
        )

        responses.add(
            responses.GET,
            'https://example.com',
            body='',
            status=404
        )

        scrape_page_links(page)

        page.refresh_from_db()
        self.assertEqual(page.status, 'failed')
        self.assertIsNotNone(page.error_message)

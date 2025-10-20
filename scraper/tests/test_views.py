from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from ..models import ScrapedPage


class AuthenticationViewsTest(TestCase):
    """Test authentication views"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='testpass123'
        )

    def test_register_view_get(self):
        """Test register view GET request"""
        response = self.client.get(reverse('scraper:register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create Your Account')

    def test_register_view_post_success(self):
        """Test successful user registration"""
        response = self.client.post(reverse('scraper:register'), {
            'email': 'newuser@example.com',
            'password1': 'complexpass123',
            'password2': 'complexpass123'
        })
        self.assertRedirects(response, reverse('scraper:page_list'))

        # Check user was created
        self.assertTrue(
            User.objects.filter(email='newuser@example.com').exists()
        )

    def test_register_view_post_duplicate_email(self):
        """Test registration with duplicate email"""
        response = self.client.post(reverse('scraper:register'), {
            'email': 'test@example.com',
            'password1': 'complexpass123',
            'password2': 'complexpass123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'already exists')

    def test_login_view_get(self):
        """Test login view GET request"""
        response = self.client.get(reverse('scraper:login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Login to web scraper')

    def test_login_view_post_success(self):
        """Test successful login"""
        response = self.client.post(reverse('scraper:login'), {
            'username': 'test@example.com',
            'password': 'testpass123'
        })
        self.assertRedirects(response, reverse('scraper:page_list'))

    def test_login_view_post_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = self.client.post(reverse('scraper:login'), {
            'username': 'test@example.com',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid email or password')

    def test_logout_view_get(self):
        """Test logout view with GET request"""
        # First login
        self.client.login(username='test@example.com', password='testpass123')

        # Test logout
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('login'))

        # Verify user is logged out by trying to access protected page
        response = self.client.get(reverse('scraper:page_list'))
        self.assertRedirects(response, '/accounts/login/?next=/pages/')

    def test_logout_view_post(self):
        """Test logout view with POST request"""
        # First login
        self.client.login(username='test@example.com', password='testpass123')

        # Test logout
        response = self.client.post(reverse('logout'))
        self.assertRedirects(response, reverse('login'))

        # Verify user is logged out
        response = self.client.get(reverse('scraper:page_list'))
        self.assertRedirects(response, '/accounts/login/?next=/pages/')

    def test_logout_view_when_not_logged_in(self):
        """Test logout view when user is not logged in"""
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('login'))


class ScraperViewsTest(TestCase):
    """Test scraper views"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='testpass123'
        )

    def test_page_list_requires_login(self):
        """Test page list view requires authentication"""
        response = self.client.get(reverse('scraper:page_list'))
        self.assertRedirects(response, '/accounts/login/?next=/pages/')

    def test_page_list_authenticated(self):
        """Test page list view for authenticated user"""
        self.client.login(username='test@example.com', password='testpass123')
        response = self.client.get(reverse('scraper:page_list'))
        self.assertEqual(response.status_code, 200)

    def test_page_detail_requires_login(self):
        """Test page detail view requires authentication"""
        page = ScrapedPage.objects.create(
            user=self.user,
            url='https://example.com',
            title='Test Page'
        )
        response = self.client.get(
            reverse('scraper:page_detail', kwargs={'pk': page.pk})
        )
        self.assertRedirects(
            response, f'/accounts/login/?next=/pages/{page.pk}/')

    def test_page_detail_authenticated(self):
        """Test page detail view for authenticated user"""
        self.client.login(username='test@example.com', password='testpass123')
        page = ScrapedPage.objects.create(
            user=self.user,
            url='https://example.com',
            title='Test Page'
        )
        response = self.client.get(
            reverse('scraper:page_detail', kwargs={'pk': page.pk})
        )
        self.assertEqual(response.status_code, 200)

    def test_page_detail_other_user_page(self):
        """Test user cannot access other user's pages"""
        other_user = User.objects.create_user(
            username='other@example.com',
            email='other@example.com',
            password='testpass123'
        )
        page = ScrapedPage.objects.create(
            user=other_user,
            url='https://example.com',
            title='Other User Page'
        )

        self.client.login(username='test@example.com', password='testpass123')
        response = self.client.get(
            reverse('scraper:page_detail', kwargs={'pk': page.pk})
        )
        self.assertEqual(response.status_code, 404)

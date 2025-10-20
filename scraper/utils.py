import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
from django.utils import timezone
from .models import ScrapedPage, PageLink
from .constants import ScrapingStatus


def is_valid_url(url):
    """Check if the URL is valid"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False


def clean_link_text(text):
    """Clean and truncate link text"""
    if not text:
        return 'No text'

    # Remove extra whitespace and newlines
    text = ' '.join(text.split())

    # Truncate if too long
    if len(text) > 200:
        text = text[:197] + '...'

    return text or 'No text'


def scrape_page_links(scraped_page):
    """
    Scrape all links from a given page and save them to the database
    """
    try:
        # Update status to processing
        scraped_page.status = ScrapingStatus.PROCESSING
        scraped_page.save()

        # Set headers to mimic a real browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        # Make the request with timeout
        response = requests.get(scraped_page.url, headers=headers, timeout=30)
        response.raise_for_status()

        # Parse the HTML
        soup = BeautifulSoup(response.content, 'html.parser')

        # Get the page title
        title_tag = soup.find('title')
        if title_tag and title_tag.get_text().strip():
            scraped_page.title = title_tag.get_text().strip()[:500]
        else:
            scraped_page.title = scraped_page.url

        # Find all anchor tags with href attributes
        links = soup.find_all('a', href=True)

        # Clear existing links for this page
        scraped_page.links.all().delete()

        # Process each link
        links_created = 0
        for link in links:
            href = link.get('href')
            if not href:
                continue

            # Convert relative URLs to absolute URLs
            absolute_url = urljoin(scraped_page.url, href)

            # Skip if not a valid URL
            if not is_valid_url(absolute_url):
                continue

            # Get link text (could be text or HTML elements)
            link_text = clean_link_text(link.get_text())

            # Create the PageLink object
            try:
                PageLink.objects.get_or_create(
                    page=scraped_page,
                    url=absolute_url,
                    defaults={'name': link_text}
                )
                links_created += 1
            except Exception as e:
                # Skip duplicate or invalid links
                continue

        # Update status to completed
        scraped_page.status = ScrapingStatus.COMPLETED
        scraped_page.error_message = None
        scraped_page.updated_at = timezone.now()
        scraped_page.save()

        return links_created

    except requests.exceptions.RequestException as e:
        # Handle network-related errors
        scraped_page.status = ScrapingStatus.FAILED
        scraped_page.error_message = f'Network error: {str(e)}'
        scraped_page.save()
        return 0

    except Exception as e:
        # Handle other errors
        scraped_page.status = ScrapingStatus.FAILED
        scraped_page.error_message = f'Error: {str(e)}'
        scraped_page.save()
        return 0


def scrape_page_async(scraped_page_id):
    """
    Async wrapper for scraping (can be used with background tasks)
    """
    try:
        scraped_page = ScrapedPage.objects.get(id=scraped_page_id)
        return scrape_page_links(scraped_page)
    except ScrapedPage.DoesNotExist:
        return 0

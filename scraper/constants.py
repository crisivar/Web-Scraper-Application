"""
Constants used throughout the scraper application
"""

# Scraping status constants
class ScrapingStatus:
    PENDING = 'pending'
    PROCESSING = 'processing'
    COMPLETED = 'completed'
    FAILED = 'failed'

# Pagination constants
PAGES_PER_PAGE = 10
LINKS_PER_PAGE = 20

# Timeout constants
DEFAULT_SCRAPING_TIMEOUT = 30
DEFAULT_REQUEST_TIMEOUT = 10

# Message constants
class Messages:
    # Success messages
    REGISTRATION_SUCCESS = 'Registration successful! Welcome to the Web Scraper.'
    LOGIN_SUCCESS = 'Welcome back!'
    LOGOUT_SUCCESS = 'You have been successfully logged out.'
    URL_ADDED_SUCCESS = 'URL added successfully! Scraping started in the background.'
    URL_SCRAPED_SUCCESS = 'URL scraped successfully!'
    RESCRAPE_SUCCESS = 'Re-scraping started successfully!'
    PAGE_DELETED_SUCCESS = 'Page deleted successfully!'

    # Error messages
    INVALID_CREDENTIALS = 'Invalid email or password.'
    REGISTRATION_LOGIN_FAILED = 'Registration successful but login failed. Please try logging in manually.'
    URL_ALREADY_EXISTS = 'This URL has already been scraped by you.'
    SCRAPING_FAILED = 'Failed to scrape URL: {}'
    RESCRAPE_FAILED = 'Failed to re-scrape page: {}'
    QUEUE_TASK_FAILED = 'Failed to queue scraping task: {}'
    QUEUE_RETASK_FAILED = 'Failed to queue re-scraping task: {}'
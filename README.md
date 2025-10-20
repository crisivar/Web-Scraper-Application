# Web Scraper Application

A Django-based web scraping application using templates

## Features

- **User Authentication**: Register and login with username and password
- **URL Scraping**: Add URLs to scrape and extract all `<a>` tag links
- **Page Management**: View list of all scraped pages with link counts
- **Link Details**: See detailed view of all links found on each page
- **Background Processing**: Large pages are scraped asynchronously using Celery
- **Task Monitoring**: Monitor background task status with Flower
- **Responsive Design**: Mobile-friendly Bootstrap interface

## Quick Start

**Prerequisites**: Docker Engine and Docker Compose must be installed and running.

- Install Docker Desktop: <https://docs.docker.com/get-docker/>

1. **Clone and setup**:

   ```bash
   git clone https://github.com/crisivar/Web-Scraper-Application.git
   cd Web-Scraper-Application
   cp .env.example .env
   ```

2. **Start the application** (Full Docker setup):

   ```bash
   docker compose up --build
   ```

3. **Alternative: Local development** (Django locally, Redis in Docker):

   ```bash
   # Start only Redis
   docker compose -f docker-compose.local.yml up -d

   # Setup local environment
   cp .env.local.example .env.local

   # Create and activate virtual environment
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate

   # Install dependencies
   pip install -r requirements.txt

   # Run Django locally
   python manage.py migrate
   python manage.py runserver
   ```

4. **Access the application**:
   - **Main app**: <http://localhost:8000>
   - **Task monitoring (Flower)**: <http://localhost:5555>

The application includes:

- ✅ PostgreSQL database with automatic setup
- ✅ Redis for background tasks
- ✅ Celery workers for scraping
- ✅ Flower monitoring dashboard
- ✅ User registration and authentication system
- ✅ All migrations applied automatically

## Usage

1. **Visit** <http://localhost:8000> - you'll be redirected to login if not authenticated
2. **Register** a new account or login with existing credentials
3. **Add a URL** to scrape using the form on the main page
4. **Wait for processing** - scraping happens in the background
5. **View results** by clicking on the page to see all extracted links

### How It Works

1. **User submits URL**: Form validation ensures URL format is correct
2. **Background task created**: Celery queues the scraping task
3. **Web scraping process**:
   - Requests library fetches the webpage content
   - BeautifulSoup4 parses HTML and extracts all `<a>` tags
   - Links are converted to absolute URLs
   - Page title and link text are captured
4. **Data storage**: Results saved to PostgreSQL database
5. **Real-time monitoring**: Track progress via Flower dashboard
6. **Results display**: View paginated lists of pages and their links

## Development Commands

### Full Docker Development

```bash

# Run tests
docker compose run --rm web python manage.py test scraper.tests
```

### Running Tests

```bash
# Run all tests
docker compose run --rm web python manage.py test scraper.tests --verbosity=2

# Run specific test file
docker compose run --rm web python manage.py test scraper.tests.test_backends
docker compose run --rm web python manage.py test scraper.tests.test_forms
docker compose run --rm web python manage.py test scraper.tests.test_models
docker compose run --rm web python manage.py test scraper.tests.test_utils
docker compose run --rm web python manage.py test scraper.tests.test_views
docker compose run --rm web python manage.py test scraper.tests.test_settings
```

## Service Architecture

The application uses a multi-container setup with clear separation of concerns:

- **`django-setup`**: One-time initialization service

  - Runs database migrations
  - Exits after completion (`restart: "no"`)

- **`web`**: Main Django application server

  - Runs the development server on port 8000
  - Depends on setup completion before starting

- **`worker`**: Celery background task processor

  - Handles web scraping tasks asynchronously
  - Depends on setup completion before starting

- **`flower`**: Celery monitoring dashboard

  - Web interface for monitoring background tasks
  - Available on port 5555

- **`db`**: PostgreSQL database
- **`redis`**: Message broker for Celery

## Technologies & Tools Used

### Backend Framework

- **Django 5.2+**: Main web framework for the application
  - Provides user authentication, ORM, and web server
  - Handles HTTP requests, routing, and database interactions

### Database & Caching

- **PostgreSQL 15**: Primary database for storing scraped pages and links. Stores user accounts, scraped pages, and extracted link data
- **Redis 7**: In-memory cache and message broker
  - Powers Celery task queues for background processing
  - Fast key-value store for temporary data and job queues

### Background Processing

- **Celery 5.5+**: Distributed task queue system
  - Handles web scraping tasks asynchronously in the background
  - Prevents web interface from blocking during long scraping operations
  - Supports task retries and error handling
- **Flower**: Web-based monitoring tool for Celery
  - Real-time monitoring of background tasks and workers
  - View task status, execution times, and queue information

### Web Scraping

- **Requests**: HTTP library for fetching web pages
  - Handles HTTP requests to target websites
  - Supports headers, timeouts, and error handling
- **BeautifulSoup4**: HTML parsing library
  - Extracts links (`<a>` tags) from scraped web pages
  - Parses HTML content and finds specific elements

### Frontend & UI

- **Bootstrap 5.3.3**: CSS framework for responsive design

- **Django Templates**: Server-side templating system

### Security & Configuration

- **python-dotenv**: Environment variable management
  - Loads sensitive configuration from `.env` files
  - Keeps secrets out of source code
- **dj-database-url**: Database URL parsing
  - Simplifies database configuration from environment variables

## Developer

**Cristian Ivan Rojas**
<crisivar@gmail.com>

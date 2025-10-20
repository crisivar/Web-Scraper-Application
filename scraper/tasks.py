from celery import shared_task, current_app
from celery.result import AsyncResult
from .models import ScrapedPage
from .utils import scrape_page_links
from .constants import ScrapingStatus, Messages
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 60})
def scrape_page_task(self, scraped_page_id):
    """
    Celery task to scrape a page asynchronously
    """
    try:
        scraped_page = ScrapedPage.objects.get(id=scraped_page_id)
        logger.info(
            f"Starting async scraping for page {scraped_page_id}: {scraped_page.url}")

        # Update task ID in the model
        scraped_page.job_id = self.request.id
        scraped_page.save()

        # Call the scraping function
        links_count = scrape_page_links(scraped_page)

        logger.info(
            f"Completed async scraping for page {scraped_page_id}. Found {links_count} links.")
        return {
            'success': True,
            'links_count': links_count,
            'page_id': scraped_page_id,
            'status': scraped_page.status,
            'task_id': self.request.id
        }

    except ScrapedPage.DoesNotExist:
        logger.error(f"ScrapedPage with id {scraped_page_id} does not exist")
        return {
            'success': False,
            'error': f'Page with id {scraped_page_id} not found',
            'task_id': self.request.id
        }
    except Exception as e:
        logger.error(
            f"Error in async scraping for page {scraped_page_id}: {str(e)}")
        # Update the page status to failed
        try:
            scraped_page = ScrapedPage.objects.get(id=scraped_page_id)
            scraped_page.status = ScrapingStatus.FAILED
            scraped_page.error_message = str(e)
            scraped_page.save()
        except ScrapedPage.DoesNotExist:
            pass

        # Re-raise for Celery retry mechanism
        raise self.retry(exc=e, countdown=60, max_retries=3)


def queue_scraping_task(scraped_page_id):
    """
    Queue a scraping task for background processing using Celery
    """
    try:
        task = scrape_page_task.delay(scraped_page_id)
        logger.info(
            f"Queued scraping task for page {scraped_page_id} with task id {task.id}")
        return task

    except Exception as e:
        logger.error(
            f"Failed to queue scraping task for page {scraped_page_id}: {str(e)}")
        raise


def get_task_status(task_id):
    """
    Get the status of a Celery task
    """
    try:
        result = AsyncResult(task_id)

        return {
            'id': task_id,
            'status': result.status,
            'result': result.result,
            'traceback': result.traceback,
            'ready': result.ready(),
            'successful': result.successful(),
            'failed': result.failed(),
        }
    except Exception:
        return None


def get_queue_stats():
    """
    Get statistics about the Celery queues
    """
    try:
        # Get active tasks
        active_tasks = current_app.control.inspect().active()
        scheduled_tasks = current_app.control.inspect().scheduled()

        stats = {
            'active_tasks': 0,
            'scheduled_tasks': 0,
            'worker_stats': {}
        }

        if active_tasks:
            for worker, tasks in active_tasks.items():
                stats['active_tasks'] += len(tasks)
                stats['worker_stats'][worker] = {
                    'active': len(tasks)
                }

        if scheduled_tasks:
            for worker, tasks in scheduled_tasks.items():
                stats['scheduled_tasks'] += len(tasks)
                if worker in stats['worker_stats']:
                    stats['worker_stats'][worker]['scheduled'] = len(tasks)
                else:
                    stats['worker_stats'][worker] = {'scheduled': len(tasks)}

        return stats

    except Exception as e:
        logger.error(f"Failed to get queue stats: {str(e)}")
        return {
            'active_tasks': 0,
            'scheduled_tasks': 0,
            'worker_stats': {},
            'error': str(e)
        }

import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web_scraping_app.settings')

app = Celery('web_scraping_app')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.update(
    task_routes={
        'scraper.tasks.scrape_page_task': {'queue': 'scraping'},
    },
    worker_hijack_root_logger=False,
    worker_preload=True,
)


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

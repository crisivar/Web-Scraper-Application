from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from .constants import ScrapingStatus


class ScrapedPage(models.Model):
    STATUS_CHOICES = [
        (ScrapingStatus.PENDING, 'Pending'),
        (ScrapingStatus.PROCESSING, 'Processing'),
        (ScrapingStatus.COMPLETED, 'Completed'),
        (ScrapingStatus.FAILED, 'Failed'),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='scraped_pages')
    url = models.URLField(max_length=2000)
    title = models.CharField(max_length=500, blank=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=ScrapingStatus.PENDING)
    job_id = models.CharField(max_length=100, blank=True,
                              null=True, help_text="Background job ID for tracking")
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['user', 'url']

    def __str__(self):
        return f"{self.title or self.url} - {self.user.username}"

    def get_absolute_url(self):
        return reverse('scraper:page_detail', kwargs={'pk': self.pk})

    @property
    def link_count(self):
        return self.links.count()


class PageLink(models.Model):
    page = models.ForeignKey(
        ScrapedPage, on_delete=models.CASCADE, related_name='links')
    url = models.URLField(max_length=2000)
    name = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        unique_together = ['page', 'url']

    def __str__(self):
        return f"{self.name[:50]}... - {self.url[:50]}..."

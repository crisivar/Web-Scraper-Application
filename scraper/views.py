from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.conf import settings
from celery.exceptions import WorkerLostError, Retry
from .models import ScrapedPage, PageLink
from .forms import CustomUserCreationForm, AddUrlForm, EmailAuthenticationForm
from .utils import scrape_page_links
from .tasks import queue_scraping_task, get_queue_stats
from .constants import ScrapingStatus, PAGES_PER_PAGE, LINKS_PER_PAGE, Messages
import logging

logger = logging.getLogger(__name__)


def handle_scraping_task(scraped_page, request, is_rescrape=False):
    """
    Helper function to handle scraping task creation with proper error handling
    """
    try:
        task = queue_scraping_task(scraped_page.id)
        scraped_page.job_id = task.id
        scraped_page.save()

        action = "re-scraping" if is_rescrape else "scraping"
        logger.info(f"Queued {action} task for page {scraped_page.id} with task {task.id}")

        success_msg = Messages.RESCRAPE_SUCCESS if is_rescrape else Messages.URL_ADDED_SUCCESS
        messages.success(request, success_msg)
        return True

    except (WorkerLostError, Retry) as e:
        # Celery-specific errors
        error_msg = Messages.QUEUE_RETASK_FAILED if is_rescrape else Messages.QUEUE_TASK_FAILED
        logger.error(error_msg.format(e))
        return False

    except Exception as e:
        # Other unexpected errors
        error_msg = Messages.QUEUE_RETASK_FAILED if is_rescrape else Messages.QUEUE_TASK_FAILED
        logger.error(error_msg.format(e))
        return False


def fallback_synchronous_scraping(scraped_page, request):
    """
    Fallback to synchronous scraping when Celery is unavailable
    """
    scraped_page.status = ScrapingStatus.PROCESSING
    scraped_page.save()

    try:
        scrape_page_links(scraped_page)
        messages.success(request, Messages.URL_SCRAPED_SUCCESS)
    except Exception as scrape_error:
        messages.error(request, Messages.SCRAPING_FAILED.format(scrape_error))


def register_view(request):
    """User registration view"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Authenticate and login the user
            authenticated_user = authenticate(
                request,
                username=user.email,
                password=form.cleaned_data['password1']
            )
            if authenticated_user:
                login(request, authenticated_user)
                messages.success(request, Messages.REGISTRATION_SUCCESS)
                return redirect('scraper:page_list')
            else:
                messages.error(request, Messages.REGISTRATION_LOGIN_FAILED)
                return redirect('login')
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/register.html', {'form': form})


def login_view(request):
    """Custom login view using email instead of username"""
    if request.method == 'POST':
        form = EmailAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')  # username field contains email
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, Messages.LOGIN_SUCCESS)
                next_url = request.GET.get('next', 'scraper:page_list')
                return redirect(next_url)
            else:
                messages.error(request, Messages.INVALID_CREDENTIALS)
        else:
            messages.error(request, Messages.INVALID_CREDENTIALS)
    else:
        form = EmailAuthenticationForm()

    return render(request, 'registration/login.html', {'form': form})


@login_required
def page_list_view(request):
    """Display list of scraped pages for the current user"""
    pages = ScrapedPage.objects.filter(user=request.user)

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        pages = pages.filter(
            Q(title__icontains=search_query) |
            Q(url__icontains=search_query)
        )

    # Pagination
    paginator = Paginator(pages, PAGES_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Handle new URL submission
    if request.method == 'POST':
        form = AddUrlForm(request.POST)
        if form.is_valid():
            scraped_page = form.save(commit=False)
            scraped_page.user = request.user

            # Check if URL already exists for this user
            existing_page = ScrapedPage.objects.filter(
                user=request.user,
                url=scraped_page.url
            ).first()

            if existing_page:
                messages.warning(request, Messages.URL_ALREADY_EXISTS)
                return redirect('scraper:page_detail', pk=existing_page.pk)

            scraped_page.save()

            # Queue scraping task for background processing
            if not handle_scraping_task(scraped_page, request):
                # Fallback to synchronous scraping
                fallback_synchronous_scraping(scraped_page, request)

            return redirect('scraper:page_detail', pk=scraped_page.pk)
    else:
        form = AddUrlForm()

    context = {
        'page_obj': page_obj,
        'form': form,
        'search_query': search_query,
        'total_pages': pages.count(),
    }

    return render(request, 'scraper/page_list.html', context)


@login_required
def page_detail_view(request, pk):
    """Display details of a specific scraped page and its links"""
    page = get_object_or_404(ScrapedPage, pk=pk, user=request.user)
    links = page.links.all()

    # Search functionality for links
    search_query = request.GET.get('search', '')
    if search_query:
        links = links.filter(
            Q(name__icontains=search_query) |
            Q(url__icontains=search_query)
        )

    # Pagination for links
    paginator = Paginator(links, LINKS_PER_PAGE)
    page_number = request.GET.get('page')
    links_page_obj = paginator.get_page(page_number)

    context = {
        'page': page,
        'links_page_obj': links_page_obj,
        'search_query': search_query,
        'total_links': links.count(),
    }

    return render(request, 'scraper/page_detail.html', context)


@login_required
@require_POST
def rescrape_page_view(request, pk):
    """Re-scrape a page"""
    page = get_object_or_404(ScrapedPage, pk=pk, user=request.user)

    # Reset status and start scraping
    page.status = ScrapingStatus.PENDING
    page.error_message = None
    page.save()

    # Queue scraping task for background processing
    if not handle_scraping_task(page, request, is_rescrape=True):
        # Fallback to synchronous scraping
        fallback_synchronous_scraping(page, request)

    return redirect('scraper:page_detail', pk=page.pk)


@login_required
def page_status_api(request, pk):
    """API endpoint to check page scraping status"""
    page = get_object_or_404(ScrapedPage, pk=pk, user=request.user)

    return JsonResponse({
        'status': page.status,
        'link_count': page.link_count,
        'error_message': page.error_message,
        'title': page.title,
    })


@login_required
def delete_page_view(request, pk):
    """Delete a scraped page"""
    page = get_object_or_404(ScrapedPage, pk=pk, user=request.user)

    if request.method == 'POST':
        page.delete()
        messages.success(request, Messages.PAGE_DELETED_SUCCESS)
        return redirect('scraper:page_list')

    return render(request, 'scraper/confirm_delete.html', {'page': page})


@login_required
def queue_status_view(request):
    """Display Celery queue status and statistics"""
    try:
        stats = get_queue_stats()
        celery_available = stats.get(
            'active_tasks', 0) >= 0 and 'error' not in stats
        context = {
            'queue_stats': stats,
            'celery_available': celery_available
        }
    except Exception as e:
        logger.error(f"Failed to get queue stats: {str(e)}")
        context = {
            'queue_stats': {'active_tasks': 0, 'scheduled_tasks': 0, 'worker_stats': {}},
            'celery_available': False,
            'error': str(e)
        }

    return render(request, 'scraper/queue_status.html', context)


def logout_view(request):
    """Custom logout view that handles both GET and POST requests"""
    logout(request)
    messages.success(request, Messages.LOGOUT_SUCCESS)
    return redirect('/accounts/login/')

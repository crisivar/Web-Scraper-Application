from django.urls import path
from . import views

app_name = 'scraper'

urlpatterns = [
    path('', views.page_list_view, name='page_list'),
    path('pages/', views.page_list_view, name='page_list'),
    path('pages/<int:pk>/', views.page_detail_view, name='page_detail'),
    path('pages/<int:pk>/rescrape/',
         views.rescrape_page_view, name='rescrape_page'),
    path('pages/<int:pk>/delete/', views.delete_page_view, name='delete_page'),
    path('api/pages/<int:pk>/status/',
         views.page_status_api, name='page_status_api'),
    path('queue-status/', views.queue_status_view, name='queue_status'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
]


from django.urls import path, include
from scraper import views as scraper_views

urlpatterns = [
    path('', include('scraper.urls')),
    path('accounts/login/', scraper_views.login_view, name='login'),
    path('accounts/logout/', scraper_views.logout_view, name='logout'),
]

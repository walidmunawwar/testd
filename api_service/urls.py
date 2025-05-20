"""
URL configuration for api_service app.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('search/', views.NearbySearchView.as_view(), name='nearby-search'),
    path('history/', views.search_history, name='search-history'),
    path('results/<int:query_id>/', views.search_results, name='search-results'),
]
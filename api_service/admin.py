"""
Admin configuration for api_service.
"""
from django.contrib import admin
from .models import SearchQuery, SearchResult

@admin.register(SearchQuery)
class SearchQueryAdmin(admin.ModelAdmin):
    list_display = ('query', 'latitude', 'longitude', 'radius', 'created_at')
    search_fields = ('query',)
    list_filter = ('created_at',)

@admin.register(SearchResult)
class SearchResultAdmin(admin.ModelAdmin):
    list_display = ('name', 'place_id', 'address', 'rating', 'user_ratings_total')
    search_fields = ('name', 'address')
    list_filter = ('rating',)
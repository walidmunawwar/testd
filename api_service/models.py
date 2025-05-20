"""
Models for the API service.
"""
from django.db import models

class SearchQuery(models.Model):
    """نموذج لتخزين استعلامات البحث"""
    query = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    radius = models.IntegerField(default=1000)  # الشعاع الافتراضي بالأمتار
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.query} at ({self.latitude}, {self.longitude})"

class SearchResult(models.Model):
    """نموذج لتخزين نتائج البحث"""
    search_query = models.ForeignKey(SearchQuery, on_delete=models.CASCADE, related_name='results')
    place_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=512, blank=True, null=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    rating = models.FloatField(null=True, blank=True)
    user_ratings_total = models.IntegerField(null=True, blank=True)
    types = models.JSONField(default=list)
    custom_data = models.JSONField(null=True, blank=True)  # لتخزين أي بيانات إضافية تمت معالجتها
    
    def __str__(self):
        return self.name
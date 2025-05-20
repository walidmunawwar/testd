"""
Serializers for the API service.
"""
from rest_framework import serializers
from .models import SearchQuery, SearchResult

class SearchResultSerializer(serializers.ModelSerializer):
    """مسلسل لنتائج البحث"""
    class Meta:
        model = SearchResult
        fields = ['id', 'place_id', 'name', 'address', 'latitude', 'longitude', 
                  'rating', 'user_ratings_total', 'types', 'custom_data']

class SearchQuerySerializer(serializers.ModelSerializer):
    """مسلسل لاستعلام البحث"""
    results = SearchResultSerializer(many=True, read_only=True)
    
    class Meta:
        model = SearchQuery
        fields = ['id', 'query', 'latitude', 'longitude', 'radius', 'created_at', 'results']
        read_only_fields = ['created_at']

class ExternalAPIRequestSerializer(serializers.Serializer):
    """مسلسل لطلبات API الخارجي"""
    prompt = serializers.CharField(required=True)
    # تمت إزالة الحقول الأخرى واستبدالها بحقل prompt فقط

class PlaceResultSerializer(serializers.Serializer):
    """مسلسل لنتائج المكان من API الخارجي"""
    place_id = serializers.CharField()
    name = serializers.CharField()
    address = serializers.CharField(required=False, allow_null=True)
    location = serializers.DictField()
    rating = serializers.FloatField(required=False, allow_null=True)
    user_ratings_total = serializers.IntegerField(required=False, allow_null=True)
    types = serializers.ListField(child=serializers.CharField(), required=False)
    
    # يمكنك إضافة حقول مخصصة إضافية هنا حسب ما تحتاج
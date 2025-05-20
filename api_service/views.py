"""
Views for the API service.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from django.db import transaction

from .serializers import (
    ExternalAPIRequestSerializer, 
    SearchQuerySerializer,
    SearchResultSerializer
)
from .services import ExternalAPIService
from .models import SearchQuery, SearchResult

class NearbySearchView(APIView):
    """واجهة للبحث عن الأماكن القريبة"""
    
    def post(self, request):
        # التحقق من صحة البيانات المدخلة
        serializer = ExternalAPIRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # استخراج البيانات المتحقق منها
        query = serializer.validated_data['query']
        latitude = serializer.validated_data['latitude']
        longitude = serializer.validated_data['longitude']
        radius = serializer.validated_data.get('radius', 1000)
        
        # استدعاء API الخارجي
        try:
            raw_results = ExternalAPIService.search_nearby(
                query=query,
                latitude=latitude,
                longitude=longitude,
                radius=radius
            )
            
            # معالجة النتائج وإضافة معلومات إضافية
            processed_results = ExternalAPIService.process_results(raw_results)
            
            # حفظ الاستعلام والنتائج في قاعدة البيانات (معاملة واحدة)
            with transaction.atomic():
                # حفظ استعلام البحث
                search_query = SearchQuery.objects.create(
                    query=query,
                    latitude=latitude,
                    longitude=longitude,
                    radius=radius
                )
                
                # حفظ نتائج البحث إذا كانت موجودة
                if 'results' in processed_results and processed_results['results']:
                    for result in processed_results['results']:
                        # استخراج البيانات الأساسية
                        SearchResult.objects.create(
                            search_query=search_query,
                            place_id=result.get('place_id', ''),
                            name=result.get('name', ''),
                            address=result.get('address', ''),
                            latitude=result.get('location', {}).get('lat', 0),
                            longitude=result.get('location', {}).get('lng', 0),
                            rating=result.get('rating'),
                            user_ratings_total=result.get('user_ratings_total'),
                            types=result.get('types', []),
                            custom_data={
                                'quality': result.get('quality'),
                                'distance_info': result.get('distance_info'),
                                # يمكنك إضافة المزيد من البيانات المخصصة هنا
                            }
                        )
            
            # إرجاع النتائج المعالجة للمستخدم
            return Response(processed_results, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@api_view(['GET'])
def search_history(request):
    """استرجاع تاريخ البحث"""
    search_queries = SearchQuery.objects.all().order_by('-created_at')
    serializer = SearchQuerySerializer(search_queries, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def search_results(request, query_id):
    """استرجاع نتائج بحث محددة"""
    try:
        search_query = SearchQuery.objects.get(pk=query_id)
    except SearchQuery.DoesNotExist:
        return Response(
            {'error': 'استعلام البحث غير موجود'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    results = SearchResult.objects.filter(search_query=search_query)
    serializer = SearchResultSerializer(results, many=True)
    return Response(serializer.data)
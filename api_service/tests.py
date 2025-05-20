"""
Tests for the API service.
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from unittest.mock import patch

from .models import SearchQuery, SearchResult
from .services import ExternalAPIService

class NearbySearchViewTests(TestCase):
    """اختبارات لـ NearbySearchView"""
    
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('nearby-search')
        self.valid_payload = {
            "query": "مطاعم",
            "latitude": 24.7136,
            "longitude": 46.6753,  # إحداثيات الرياض
            "radius": 1000
        }
        
    @patch('api_service.services.ExternalAPIService.search_nearby')
    def test_create_search_with_valid_data(self, mock_search_nearby):
        """اختبار إنشاء بحث بنجاح مع بيانات صحيحة"""
        # تهيئة الاستجابة الوهمية
        mock_response = {
            "results": [
                {
                    "place_id": "test_place_id",
                    "name": "مطعم اختبار",
                    "address": "شارع الاختبار، الرياض",
                    "location": {"lat": 24.7136, "lng": 46.6753},
                    "rating": 4.5,
                    "user_ratings_total": 100,
                    "types": ["restaurant", "food"]
                }
            ]
        }
        mock_search_nearby.return_value = mock_response
        
        # إرسال الطلب
        response = self.client.post(self.url, self.valid_payload, format='json')
        
        # التحقق من النتائج
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('results' in response.data)
        self.assertEqual(len(response.data['results']), 1)
        
        # التحقق من حفظ البيانات في قاعدة البيانات
        self.assertEqual(SearchQuery.objects.count(), 1)
        self.assertEqual(SearchResult.objects.count(), 1)
        
    def test_create_search_with_invalid_data(self):
        """اختبار الفشل عند إدخال بيانات غير صحيحة"""
        invalid_payload = {
            "query": "مطاعم",
            # بدون latitude و longitude
            "radius": 1000
        }
        response = self.client.post(self.url, invalid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class SearchHistoryTests(TestCase):
    """اختبارات لواجهة تاريخ البحث"""
    
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('search-history')
        
        # إنشاء بعض بيانات الاختبار
        search_query = SearchQuery.objects.create(
            query="مطاعم",
            latitude=24.7136,
            longitude=46.6753,
            radius=1000
        )
        
        SearchResult.objects.create(
            search_query=search_query,
            place_id="test_place_id",
            name="مطعم اختبار",
            address="شارع الاختبار، الرياض",
            latitude=24.7136,
            longitude=46.6753,
            rating=4.5,
            user_ratings_total=100,
            types=["restaurant", "food"]
        )
    
    def test_get_search_history(self):
        """اختبار الحصول على تاريخ البحث"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # تاريخ بحث واحد

class ExternalAPIServiceTests(TestCase):
    """اختبارات لخدمة API الخارجي"""
    
    @patch('requests.post')
    def test_search_nearby(self, mock_post):
        """اختبار البحث عن الأماكن القريبة"""
        # تهيئة الاستجابة الوهمية
        mock_response = mock_post.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [
                {
                    "place_id": "test_place_id",
                    "name": "مطعم اختبار"
                    # باقي البيانات...
                }
            ]
        }
        
        # استدعاء الخدمة
        result = ExternalAPIService.search_nearby(
            query="مطاعم",
            latitude=24.7136,
            longitude=46.6753,
            radius=1000
        )
        
        # التحقق من النتائج
        self.assertTrue('results' in result)
        self.assertEqual(len(result['results']), 1)
"""
Services for interacting with external APIs.
"""
import requests
import json
from django.conf import settings
from rest_framework.exceptions import APIException

class ExternalAPIService:
    """خدمة للتفاعل مع API الخارجي لـ Google Maps"""
    
    @staticmethod
    def search_nearby(query, latitude, longitude, radius=1000):
        """
        البحث عن الأماكن القريبة باستخدام API الخارجي
        
        Args:
            query (str): استعلام البحث
            latitude (float): خط العرض
            longitude (float): خط الطول
            radius (int): شعاع البحث بالأمتار (افتراضيًا 1000 متر)
            
        Returns:
            dict: بيانات الاستجابة من API
        """
        api_url = settings.EXTERNAL_API['URL']
        
        # تجهيز بيانات الطلب
        payload = {
            "query": query,
            "latitude": latitude,
            "longitude": longitude,
            "radius": radius
        }
        
        try:
            # إرسال الطلب إلى API الخارجي
            response = requests.post(api_url, json=payload)
            
            # التحقق من نجاح الطلب
            response.raise_for_status()
            
            # تحويل الاستجابة إلى JSON
            return response.json()
            
        except requests.exceptions.RequestException as e:
            # معالجة الأخطاء المتعلقة بالطلب
            raise APIException(f"خطأ في الاتصال بـ API الخارجي: {str(e)}")
        
        except json.JSONDecodeError:
            # معالجة أخطاء تنسيق JSON
            raise APIException("تعذر تحليل استجابة API الخارجي")

    @staticmethod
    def process_results(raw_results):
        """
        معالجة البيانات الواردة من API الخارجي وإضافة معلومات إضافية مفيدة
        
        Args:
            raw_results (dict): البيانات الخام من API
            
        Returns:
            dict: البيانات المعالجة
        """
        # نسخة من البيانات الأصلية
        processed_results = raw_results.copy()
        
        # التحقق من وجود نتائج
        if 'results' not in processed_results or not processed_results['results']:
            return processed_results
        
        # معالجة كل نتيجة
        for i, result in enumerate(processed_results['results']):
            # إضافة معلومات تحليلية إضافية
            if 'rating' in result:
                # إضافة تصنيف مخصص بناءً على التقييم
                rating = result['rating']
                if rating >= 4.5:
                    result['quality'] = "ممتاز"
                elif rating >= 4.0:
                    result['quality'] = "جيد جداً"
                elif rating >= 3.5:
                    result['quality'] = "جيد"
                elif rating >= 3.0:
                    result['quality'] = "متوسط"
                else:
                    result['quality'] = "دون المتوسط"
            
            # حساب المسافة التقريبية (يمكنك تنفيذ حساب أكثر دقة)
            if 'location' in result:
                # هذا مجرد مثال بسيط - في التطبيق الفعلي ستحتاج إلى حساب المسافة الحقيقية
                result['distance_info'] = {
                    'from_center': f"{i * 100 + 50} متر تقريباً",  # مثال توضيحي فقط
                }
            
            # يمكنك إضافة المزيد من المعالجات حسب احتياجاتك
        
        return processed_results
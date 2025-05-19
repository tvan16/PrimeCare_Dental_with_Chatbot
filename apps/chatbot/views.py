from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import os
from .templatetags.chatbot import DentalChatbot, DataProcessor

# Lấy đường dẫn tuyệt đối đến thư mục data
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, 'data')

# Khởi tạo chatbot instance
data_processor = DataProcessor(
    dental_path=os.path.join(DATA_DIR, 'news-detail.json'),
    doctor_path=os.path.join(DATA_DIR, 'doctors.json'),
    price_path=os.path.join(DATA_DIR, 'service-prices.json'),
    financial_path=os.path.join(DATA_DIR, 'financial_services.json')
)
chatbot = DentalChatbot(data_processor)

@csrf_exempt
@require_http_methods(["POST"])
def chatbot_api(request):
    try:
        data = json.loads(request.body)
        message = data.get('message', '')
        
        if not message:
            return JsonResponse({
                'error': 'No message provided'
            }, status=400)
            
        # Xử lý tin nhắn qua chatbot
        result = chatbot.process_query(message)
        
        return JsonResponse({
            'response': result['response'],
            'agent_type': result['agent_type']
        })
        
    except Exception as e:
        print(f"Error in chatbot_api: {str(e)}")  # Thêm log để debug
        return JsonResponse({
            'error': str(e)
        }, status=500)

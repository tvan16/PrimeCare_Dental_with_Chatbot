import os
from django import template
from django.conf import settings
import random
import json
register = template.Library()

@register.filter
def is_list(value):
    """Kiểm tra xem một giá trị có phải là list hoặc tuple không"""
    return isinstance(value, list) or isinstance(value, tuple)

@register.filter
def is_dict(value):
    """Kiểm tra xem một giá trị có phải là dictionary không"""
    return isinstance(value, dict)

@register.filter(name='split')
def split(value, key):
    """
    Tách chuỗi thành danh sách dựa trên key
    Ví dụ với value="a.b.c" và key=".", kết quả là ['a', 'b', 'c']
    """
    if value:
        return value.split(key)
    return []

@register.filter(name='strip')
def strip(value):
    """Loại bỏ khoảng trắng thừa đầu và cuối chuỗi"""
    if value:
        return value.strip()
    return ''
@register.filter
def multiply(value, arg):
    """Nhân số với một giá trị"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return ''

@register.filter
def file_exists(file_path):
    """Kiểm tra file có tồn tại không"""
    # Tìm trong thư mục STATIC_ROOT
    if settings.STATIC_ROOT:
        static_path = os.path.join(settings.STATIC_ROOT, file_path)
        if os.path.isfile(static_path):
            return True
    
    # Tìm trong các thư mục STATICFILES_DIRS
    for static_dir in getattr(settings, 'STATICFILES_DIRS', []):
        path = os.path.join(static_dir, file_path)
        if os.path.isfile(path):
            return True
            
    return False

@register.filter
def add(value, arg):
    """Thêm giá trị vào một chuỗi khác"""
    try:
        return str(value) + str(arg)
    except (ValueError, TypeError):
        return value
@register.filter(name='isinstance')
def isinstance_filter(value, arg):
    """Kiểm tra kiểu dữ liệu của một biến"""
    if arg == 'dict':
        return isinstance(value, dict)
    elif arg == 'list':
        return isinstance(value, list)
    elif arg == 'string' or arg == 'str':
        return isinstance(value, str)
    return False

@register.filter(name='get_item')
def get_item(dictionary, key):
    """Lấy giá trị từ dict theo key"""
    if dictionary is None:
        return None
    return dictionary.get(key, None)
import os
import django
import json
import sys
import re

# Thiết lập môi trường Django
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primecare.settings')

try:
    django.setup()
    print("Django đã được khởi tạo thành công")
except Exception as e:
    print(f"Lỗi khởi tạo Django: {str(e)}")
    sys.exit(1)

from apps.doctors.models import Doctor

def clean_text(text):
    """Hàm làm sạch văn bản: loại bỏ dấu [], '' và khoảng trắng thừa"""
    if not isinstance(text, str):
        text = str(text)
    
    # Loại bỏ dấu ngoặc vuông ở đầu và cuối nếu có
    text = re.sub(r'^\s*\[\s*|\s*\]\s*$', '', text)
    
    # Loại bỏ dấu nháy đơn ở đầu và cuối nếu có
    text = re.sub(r'^\s*\'|\'\s*$', '', text)
    text = re.sub(r'^\s*\"|\"\s*$', '', text)
    
    # Cắt khoảng trắng thừa
    text = text.strip()
    
    return text

def fix_doctor_data():
    """Cập nhật dữ liệu bác sĩ từ JSON vào database"""
    
    # Đường dẫn tới file JSON chứa dữ liệu bác sĩ
    json_file_path = os.path.join(BASE_DIR, 'data', 'doctors.json')
    
    if not os.path.exists(json_file_path):
        print(f"Không tìm thấy file JSON tại: {json_file_path}")
        return
    
    # Đọc dữ liệu từ file JSON
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            doctors_data = json.load(f)
            print(f"Đã đọc dữ liệu của {len(doctors_data)} bác sĩ từ file JSON")
    except Exception as e:
        print(f"Lỗi khi đọc file JSON: {str(e)}")
        return
    
    # Cập nhật dữ liệu cho từng bác sĩ
    updated_count = 0
    for doctor_data in doctors_data:
        try:
            # Tìm bác sĩ trong database theo tên
            name = doctor_data.get('name')
            if not name:
                print("Bỏ qua bản ghi không có tên")
                continue
                
            doctors = Doctor.objects.filter(name=name)
            if not doctors.exists():
                print(f"Không tìm thấy bác sĩ trong database: {name}")
                continue
            
            doctor = doctors.first()
            print(f"\nĐang cập nhật dữ liệu cho bác sĩ: {doctor.name} (ID: {doctor.id})")
            
            # Cập nhật bio_intro
            if 'bio_intro' in doctor_data:
                doctor.bio_intro = clean_text(doctor_data['bio_intro'])
                print(f"  - Đã cập nhật bio_intro: {doctor.bio_intro[:50]}...")
            
            # Cập nhật bio_expertise_1
            if 'bio_expertise_1' in doctor_data:
                doctor.bio_expertise_1 = clean_text(doctor_data['bio_expertise_1'])
                print(f"  - Đã cập nhật bio_expertise_1: {doctor.bio_expertise_1[:50]}...")
            
            # Cập nhật bio_expertise_2
            if 'bio_expertise_2' in doctor_data:
                doctor.bio_expertise_2 = clean_text(doctor_data['bio_expertise_2'])
                print(f"  - Đã cập nhật bio_expertise_2: {doctor.bio_expertise_2[:50]}...")
            
            # Cập nhật các chỉ số kỹ năng
            if 'healing_therapy' in doctor_data:
                doctor.healing_therapy = doctor_data['healing_therapy']
                print(f"  - Đã cập nhật healing_therapy: {doctor.healing_therapy}")
                
            if 'pain_management' in doctor_data:
                doctor.pain_management = doctor_data['pain_management']
                print(f"  - Đã cập nhật pain_management: {doctor.pain_management}")
                
            if 'diagnosis' in doctor_data:
                doctor.diagnosis = doctor_data['diagnosis']
                print(f"  - Đã cập nhật diagnosis: {doctor.diagnosis}")
            
            # Lưu các thay đổi vào database
            doctor.save()
            updated_count += 1
            print(f"  - Đã lưu thành công thay đổi cho bác sĩ {doctor.name}")
            
        except Exception as e:
            print(f"  - Lỗi khi cập nhật bác sĩ {doctor_data.get('name', 'unknown')}: {str(e)}")
    
    print(f"\nĐã cập nhật thành công dữ liệu cho {updated_count}/{len(doctors_data)} bác sĩ!")

if __name__ == "__main__":
    fix_doctor_data()
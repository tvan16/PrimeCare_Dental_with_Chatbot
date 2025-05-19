import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from apps.doctors.models import Doctor

class Command(BaseCommand):
    help = 'Cập nhật dữ liệu bác sĩ từ file doctors.json'

    def handle(self, *args, **options):
        # Sử dụng settings.BASE_DIR để xác định đường dẫn đúng
        json_file = os.path.join(settings.BASE_DIR, 'data', 'doctors.json')
        
        self.stdout.write(f'Đang đọc file từ: {json_file}')
        
        try:
            # Kiểm tra xem file có tồn tại không
            if not os.path.exists(json_file):
                self.stdout.write(self.style.ERROR(f'File không tồn tại: {json_file}'))
                return
                
            # Đọc file JSON
            with open(json_file, 'r', encoding='utf-8') as file:
                doctors_data = json.load(file)
                
            self.stdout.write(f'Đã đọc {len(doctors_data)} bác sĩ từ file JSON')
            
            # Đếm số lượng bác sĩ được cập nhật và tạo mới
            updated_count = 0
            created_count = 0
            
            # Duyệt qua từng bác sĩ trong dữ liệu JSON
            for doctor_data in doctors_data:
                # Lấy tên bác sĩ
                doctor_name = doctor_data.get('name')
                
                if not doctor_name:
                    self.stdout.write(self.style.WARNING('Bỏ qua bác sĩ không có tên'))
                    continue
                
                # Tìm bác sĩ theo tên hoặc tạo mới nếu không có
                doctor, created = Doctor.objects.get_or_create(name=doctor_name)
                
                # Danh sách các trường cần cập nhật
                fields = [
                    'area', 'education', 'certificate', 'image', 
                    'expertise', 'languages', 'quotes', 'bio_intro', 
                    'bio_expertise', 'bio_education', 'bio_experience'
                ]
                
                # Cập nhật thông tin bác sĩ từ dữ liệu JSON
                for field in fields:
                    if field in doctor_data:
                        setattr(doctor, field, doctor_data.get(field, ''))
                
                # Cập nhật mạng xã hội
                if 'facebook' in doctor_data:
                    doctor.facebook = doctor_data['facebook']
                if 'instagram' in doctor_data:
                    doctor.instagram = doctor_data['instagram']
                if 'x' in doctor_data:
                    doctor.twitter = doctor_data['x']
                elif 'twitter' in doctor_data:
                    doctor.twitter = doctor_data['twitter']
                
                # Lưu bác sĩ
                doctor.save()
                
                if created:
                    created_count += 1
                    self.stdout.write(f'Đã tạo bác sĩ mới: {doctor_name}')
                else:
                    updated_count += 1
                    self.stdout.write(f'Đã cập nhật bác sĩ: {doctor_name}')
                
            self.stdout.write(self.style.SUCCESS(f'Hoàn tất: {created_count} bác sĩ được tạo, {updated_count} bác sĩ được cập nhật'))
            
        except json.JSONDecodeError:
            self.stdout.write(self.style.ERROR(f'File không đúng định dạng JSON: {json_file}'))
        except PermissionError:
            self.stdout.write(self.style.ERROR(f'Không có quyền đọc file: {json_file}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Lỗi: {str(e)}'))
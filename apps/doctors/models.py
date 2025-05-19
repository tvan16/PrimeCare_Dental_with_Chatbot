import re
import unicodedata
import json
from django.db import models
from django.utils.text import slugify

class Doctor(models.Model):
    name = models.CharField(max_length=100, verbose_name="Họ và tên")
    slug = models.SlugField(max_length=255, unique=True, null=True)
    area = models.CharField(max_length=200, verbose_name="Chuyên khoa")
    education = models.TextField(verbose_name="Quá trình đào tạo")
    certificate = models.TextField(verbose_name="Chứng chỉ")
    image = models.CharField(max_length=255, verbose_name="Hình ảnh")
    facebook = models.URLField(blank=True, null=True)
    instagram = models.URLField(blank=True, null=True)
    twitter = models.URLField(blank=True, null=True, verbose_name="X (Twitter)")
    
    # Thêm trường lưu trữ nội dung tạo bởi AI
    bio_intro = models.TextField(null=True, blank=True)
    bio_generated_at = models.DateTimeField(null=True, blank=True)

    # Thêm trường mới cho phần expertise
    bio_expertise_1 = models.TextField(blank=True, null=True, verbose_name="Chuyên môn - Đoạn 1")
    bio_expertise_2 = models.TextField(blank=True, null=True, verbose_name="Chuyên môn - Đoạn 2")

    # Thêm các trường mới cho kỹ năng
    healing_therapy = models.IntegerField(default=85, verbose_name="Liệu pháp chữa lành")
    pain_management = models.IntegerField(default=80, verbose_name="Quản lý đau") 
    diagnosis = models.IntegerField(default=90, verbose_name="Kiểm tra và chẩn đoán")
    
    def save(self, *args, **kwargs):
    # Tự động tạo slug từ tên nếu không được cung cấp
        if not self.slug:
            self.slug = slugify(self.name)
        
        # Tự động tạo tên file ảnh nếu chưa có
        if not self.image:
            # Loại bỏ dấu tiếng Việt và xử lý ký tự đặc biệt
            special_chars = {
                'Đ': 'D', 'đ': 'd',
                'Ê': 'E', 'ê': 'e',
                'Ă': 'A', 'ă': 'a',
                'Ư': 'U', 'ư': 'u',
                'Ơ': 'O', 'ơ': 'o',
            }
            
            # Thay thế các ký tự đặc biệt trước
            name_copy = self.name
            for vietnamese, latin in special_chars.items():
                name_copy = name_copy.replace(vietnamese, latin)
            
            # Loại bỏ dấu tiếng Việt
            normalized = unicodedata.normalize('NFKD', name_copy)
            no_accent = ''.join([c for c in normalized if not unicodedata.combining(c)])
            
            # Loại bỏ các ký tự không phải chữ cái và số
            clean_name = re.sub(r'[^a-zA-Z0-9\s]', '', no_accent)
            
            # Viết hoa chữ cái đầu mỗi từ, loại bỏ khoảng trắng
            formatted_name = ''.join([word.capitalize() for word in clean_name.split()])
            
            # Đặt tên file
            self.image = f"{formatted_name}.png"
        
        # Chỉ gọi super().save() một lần ở cuối
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
# services/models.py
from django.db import models
from apps.doctors.models import Doctor  # Thêm ở đầu file nếu chưa có

class MainService(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    intro = models.TextField("Giới thiệu chung", blank=True)
    intro_image = models.ImageField(upload_to='main_service_images/', blank=True, null=True)
    icon = models.FileField(upload_to='main_services/icons/', blank=True, null=True)  # nếu muốn icon động
    #Giới thiệu chi tiết
    intro_detail_image = models.ImageField(upload_to='main_service_images/', blank=True, null=True)
    detail_title = models.CharField(max_length=255, default="Giới thiệu dịch vụ")
    detail_content = models.TextField("Nội dung chi tiết", blank=True)
    # Lợi ích
    benefits_title = models.CharField(max_length=255, default="Các Lợi Ích Chính")
    benefits_intro = models.TextField("Đoạn giới thiệu lợi ích", blank=True)
    benefits_list = models.TextField("Danh sách lợi ích (mỗi dòng 1 lợi ích)", blank=True)
    benefits_outro = models.TextField("Đoạn kết lợi ích", blank=True)
    benefits_image = models.ImageField(upload_to='main_service_images/', blank=True, null=True)
    
    # FAQ
    faq_title = models.CharField(max_length=255, default="Mọi điều bạn cần biết")
    faq_subtitle = models.CharField(max_length=255, blank=True, default="")
    faq_question_1 = models.CharField(max_length=255, blank=True)
    faq_answer_1 = models.TextField(blank=True)
    faq_question_2 = models.CharField(max_length=255, blank=True)
    faq_answer_2 = models.TextField(blank=True)
    faq_question_3 = models.CharField(max_length=255, blank=True)
    faq_answer_3 = models.TextField(blank=True)
    faq_question_4 = models.CharField(max_length=255, blank=True)
    faq_answer_4 = models.TextField(blank=True)
    faq_question_5 = models.CharField(max_length=255, blank=True)
    faq_answer_5 = models.TextField(blank=True)

    def get_faqs(self):
        return [
            {"question": self.faq_question_1, "answer": self.faq_answer_1},
            {"question": self.faq_question_2, "answer": self.faq_answer_2},
            {"question": self.faq_question_3, "answer": self.faq_answer_3},
            {"question": self.faq_question_4, "answer": self.faq_answer_4},
            {"question": self.faq_question_5, "answer": self.faq_answer_5},
        ]
    def __str__(self):
        return self.name

class SubService(models.Model):
    main_service = models.ForeignKey(MainService, on_delete=models.CASCADE, related_name='sub_services')
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=255)
    original_price_min = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    original_price_max = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    discount_price_min = models.DecimalField(max_digits=12, decimal_places=0, default=0 , null=True, blank=True)
    discount_price_max = models.DecimalField(max_digits=12, decimal_places=0, default=0 , null=True, blank=True)
    discount_percent = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True)

    #thêm các trường nội dung chi tiết
    

    def __str__(self):
        return self.name

class ServiceImage(models.Model):
    sub_service = models.ForeignKey(SubService, on_delete=models.CASCADE, related_name='images', null=True, blank=True)
    image = models.ImageField(upload_to='service_images/')
    is_primary = models.BooleanField(default=False)

    def __str__(self):
        if self.sub_service:
            return f"Image for {self.sub_service.name}"
        return "Service Image"
    
class Appointment(models.Model):
    full_name = models.CharField(max_length=100, verbose_name="Họ tên khách hàng")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    phone = models.CharField(max_length=20, verbose_name="Số điện thoại")
    address = models.CharField(max_length=255, blank=True, null=True, verbose_name="Địa chỉ")
    date = models.DateField(verbose_name="Ngày hẹn")
    time = models.TimeField(verbose_name="Giờ hẹn")
    reason = models.CharField(
        max_length=100,
        choices=[
            ('general', 'Khám tổng quát'),
            ('first', 'Khám lần đầu'),
            ('specific', 'Vấn đề cụ thể')
        ],
        verbose_name="Lý do khám"
    )
    service = models.ForeignKey('SubService', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Dịch vụ")
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Bác sĩ")
    note = models.TextField(blank=True, null=True, verbose_name="Ghi chú")
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Chờ xác nhận'), ('confirmed', 'Đã xác nhận'), ('cancelled', 'Đã hủy')],
        default='pending'
    )

    def __str__(self):
        return f"{self.full_name} - {self.date} {self.time} - {self.doctor.name if self.doctor else 'Không chọn bác sĩ'}"
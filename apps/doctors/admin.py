from django.contrib import admin
from django.utils.html import format_html
from .models import Doctor


# Thay vì đăng ký với admin.site mặc định, đăng ký với admin_site tùy chỉnh
@admin.register(Doctor)  # Xóa hoặc comment dòng này
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'area')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'area')
    list_filter = ('area',)
    readonly_fields = ('admin_image_preview',)
    list_per_page = 20
    
    def admin_image_preview(self, obj):
        """Hiển thị hình ảnh xem trước trong trang quản trị"""
        if obj.image:
            return format_html('<img src="/static/images/doctor_images/{}" width="100" height="auto" />', obj.image)
        return "Không có hình ảnh"
    
    admin_image_preview.short_description = 'Hình ảnh xem trước'

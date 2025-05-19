from django.apps import AppConfig

class DoctorsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.doctors'
    verbose_name = 'Quản lý Bác sĩ'  # Tên hiển thị trong admin
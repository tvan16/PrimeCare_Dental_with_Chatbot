from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy as _

class PrimeCareAdminSite(AdminSite):
    site_title = _('PrimeCare Dentist Admin')
    site_header = _('PrimeCare Dentist - Quản trị hệ thống')
    index_title = _('Quản lý phòng khám nha khoa')

admin_site = PrimeCareAdminSite(name='primecare_admin')

# Đăng ký các models từ tất cả apps
from apps.doctors.models import Doctor
from apps.doctors.admin import DoctorAdmin

from apps.services.models import MainService, SubService, ServiceImage
from apps.services.admin import SubServiceAdmin

admin_site.register(Doctor, DoctorAdmin)
admin_site.register(MainService)
admin_site.register(SubService, SubServiceAdmin)
admin_site.register(ServiceImage)

# Đăng ký blogs
from apps.blogs.models import Blog, Category, Tag
from apps.blogs.admin import BlogAdmin, CategoryAdmin, TagAdmin

admin_site.register(Blog, BlogAdmin)
admin_site.register(Category, CategoryAdmin)
admin_site.register(Tag, TagAdmin)
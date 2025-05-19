from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.doctors import views as doctor_views
from apps.services import views as service_views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # App doctors
    path('doctors/', include(('apps.doctors.urls', 'doctors'), namespace='doctors')),
    path('dat-lich/', service_views.book_appointment, name='book_appointment'),
    path('blogs/', include('apps.blogs.urls', namespace='blogs')),

    # App chatbot
    path('chatbot/', include('apps.chatbot.urls', namespace='chatbot')),

    # Trang chủ và các trang tĩnh
    path('', doctor_views.home, name='home'),
    path('about/', doctor_views.about, name='about'),
    path('contact/', doctor_views.contact, name='contact'),
    path('gallery/', doctor_views.gallery, name='gallery'),
    path('faqs/', doctor_views.faqs, name='faqs'),
    path('testimonials/', doctor_views.testimonials, name='testimonials'),
    path('price-list/', doctor_views.price_list, name='price_list'),
    # Sử dụng view service trực tiếp thay vì include apps.services.urls
    path('services-list/', service_views.service_list, name='services_list'),
    path('services-detail/', include('apps.services.urls')),
    # Các trang thông tin
    path('terms/', doctor_views.terms, name='terms'),
    path('privacy/', doctor_views.privacy, name='privacy'),
    path('support/', doctor_views.support, name='support'),
    path('dat-lich/', service_views.book_appointment, name='book_appointment'),
]

# Phục vụ static files trong môi trường phát triển
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
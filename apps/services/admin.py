from django.contrib import admin
from .models import MainService, SubService, ServiceImage, Appointment
from django import forms

class ServiceImageInline(admin.TabularInline):
    model = ServiceImage
    extra = 1

class MainServiceAdmin(admin.ModelAdmin):
    list_per_page = 20
    search_fields = ('name',)

class SubServiceAdmin(admin.ModelAdmin):
    inlines = [ServiceImageInline]
    list_display = (
       'name',
       'main_service',
       'original_price_min',
       'original_price_max',
       'discount_price_min',
       'discount_price_max',
       'discount_percent'
    )
    list_per_page = 20
    search_fields = ('name', 'main_service__name', 'description')

class AppointmentAdminForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = '__all__'
        widgets = {
            'time': forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
        }

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    form = AppointmentAdminForm
    list_display = ('full_name', 'phone', 'doctor', 'service', 'date', 'time', 'status')
    list_filter = ('doctor', 'service', 'status', 'date')
    search_fields = ('full_name', 'phone', 'email')

admin.site.register(MainService, MainServiceAdmin)
admin.site.register(SubService, SubServiceAdmin)
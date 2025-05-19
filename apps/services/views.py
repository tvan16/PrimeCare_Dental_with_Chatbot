from django.shortcuts import render, get_object_or_404, redirect
from .models import MainService , SubService, Appointment
from django.core.paginator import Paginator
from django.db.models import Case, When, F, IntegerField
from django.contrib import messages

# Trang danh sách dịch vụ
def service_list(request):
    services = MainService.objects.all()
    return render(request, 'services/list.html', {
        'services': services,
    })

# Trang chi tiết dịch vụ
def service_detail(request, slug):
    service = get_object_or_404(MainService, slug=slug)
    sort = request.GET.get('sort')
    sub_services = service.sub_services.prefetch_related('images').all()
    no_discount = False

    if sort == 'price_asc':
        sub_services = sub_services.annotate(
            effective_price_min=Case(
                When(discount_price_min__gt=0, then=F('discount_price_min')),
                default=F('original_price_min'),
                output_field=IntegerField()
            )
        ).order_by('effective_price_min')
    elif sort == 'price_desc':
        sub_services = sub_services.annotate(
            effective_price_min=Case(
                When(discount_price_min__gt=0, then=F('discount_price_min')),
                default=F('original_price_min'),
                output_field=IntegerField()
            )
        ).order_by('-effective_price_min')
    elif sort == 'discount':
        sub_services = sub_services.filter(discount_percent__gt=0)
        if not sub_services.exists():
            no_discount = True
    # Có thể bổ sung 'banchay' nếu có trường phù hợp

    paginator = Paginator(sub_services, 12)
    page_number = request.GET.get('page')
    sub_services = paginator.get_page(page_number)
    faqs = [faq for faq in service.get_faqs() if faq["question"]]
    return render(request, 'services/detail.html', {
        'service': service,
        'sub_services': sub_services,
        'faqs': faqs,
        'no_discount': no_discount,
    })

def subservice_detail(request, slug):
       sub_service = get_object_or_404(SubService, slug=slug)
       related_subservices = SubService.objects.filter(
           main_service=sub_service.main_service
       ).exclude(id=sub_service.id)[:8]
       return render(request, 'services/sub_detail.html', {
           'sub_service': sub_service,
           'related_subservices': related_subservices,
       })
# Các trang tĩnh (nếu cần)
def about(request):
    return render(request, 'pages/about-VN.html')

def contact(request):
    return render(request, 'pages/contact.html')

def faqs(request):
    return render(request, 'pages/faqs.html')

def testimonials(request):
    return render(request, 'pages/testimonials.html')

def gallery(request):
    return render(request, 'pages/gallery.html')

def terms(request):
    return render(request, 'pages/terms.html')

def privacy(request):
    return render(request, 'pages/privacy.html')

def support(request):
    return render(request, 'pages/support.html')

def price_list(request):
    return render(request, 'pages/price-list.html')

def book_appointment(request):
    if request.method == 'POST':
        print(request.POST)  # Xem dữ liệu nhận được
        full_name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('recordno')
        address = request.POST.get('location')
        date = request.POST.get('date')
        time = request.POST.get('time')
        reason_value = request.POST.get('reason')
        note = request.POST.get('note', '')

        # Map reason value from form to model choices
        if reason_value == 'Routine Checkup':
            reason = 'general'
        elif reason_value == 'New Patient Visit':
            reason = 'first'
        elif reason_value == 'Specific Concern':
            reason = 'specific'
        else:
            reason = 'general'

        Appointment.objects.create(
            full_name=full_name,
            email=email,
            phone=phone,
            address=address,
            date=date,
            time=time,
            reason=reason,
            note=note
        )
        return redirect(request.path)

    return render(request, 'includes/appointment.html')
from apps.doctors.models import Doctor

def book_doctor_appointment(request, doctor_id):
    doctor = get_object_or_404(Doctor, slug=doctor_slug)
    if request.method == 'POST':
        full_name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('recordno')
        address = request.POST.get('location')
        date = request.POST.get('date')
        time = request.POST.get('time')
        reason_value = request.POST.get('reason')
        note = request.POST.get('note', '')

        # Map reason value from form to model choices
        if reason_value == 'Routine Checkup':
            reason = 'general'
        elif reason_value == 'New Patient Visit':
            reason = 'first'
        elif reason_value == 'Specific Concern':
            reason = 'specific'
        else:
            reason = 'general'

        Appointment.objects.create(
            full_name=full_name,
            email=email,
            phone=phone,
            address=address,
            date=date,
            time=time,
            reason=reason,
            note=note,
            doctor=doctor
        )
        
    return render(request, 'includes/appointment.html', {'doctor': doctor})
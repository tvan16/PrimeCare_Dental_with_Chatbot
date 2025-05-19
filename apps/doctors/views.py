from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.utils.text import slugify
from .models import Doctor
import json
import os
from django.conf import settings
import google.generativeai as genai
from django.shortcuts import render
from datetime import datetime
import random
from django.http import JsonResponse
from django.db.models import Q

def import_doctors_from_json():
    """Import dữ liệu bác sĩ từ file JSON nếu database trống"""
    if Doctor.objects.count() == 0:
        json_file_path = os.path.join(settings.BASE_DIR, 'data', 'doctors.json')
        if os.path.exists(json_file_path):
            with open(json_file_path, 'r', encoding='utf-8') as f:
                doctors_data = json.load(f)
                
            for doctor_data in doctors_data:
                # Tạo slug từ tên bác sĩ
                name = doctor_data.get('name', '')
                slug = slugify(name)
                
                # Kiểm tra xem slug đã tồn tại chưa
                counter = 1
                base_slug = slug
                while Doctor.objects.filter(slug=slug).exists():
                    slug = f"{base_slug}-{counter}"
                    counter += 1
                
                Doctor.objects.create(
                    name=name,
                    slug=slug,
                    area=doctor_data.get('area', ''),
                    education=doctor_data.get('education', ''),
                    certificate=doctor_data.get('certificate', ''),
                    facebook=doctor_data.get('facebook', ''),
                    instagram=doctor_data.get('instagram', ''),
                    twitter=doctor_data.get('x', '')  # Sử dụng 'x' từ JSON cho trường 'twitter'
                )

def doctor_list(request):
    """Hiển thị danh sách tất cả bác sĩ với phân trang"""
    # Đảm bảo có dữ liệu
    import_doctors_from_json()
    
    # Lấy danh sách bác sĩ đã sắp xếp theo id
    all_doctors = Doctor.objects.all().order_by('id')
    
    # Phân trang: 8 bác sĩ mỗi trang
    paginator = Paginator(all_doctors, 8)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'doctors/doctor.html', {
        'page_obj': page_obj,
        'doctors': page_obj.object_list
    })

# Cấu hình Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)

def generate_doctor_bio(doctor):
    """Tạo giới thiệu bác sĩ sử dụng Gemini"""
    # Xây dựng prompt với thông tin bác sĩ
    prompt = f"""
    Tạo 2 đoạn giới thiệu chuyên nghiệp cho một bác sĩ nha khoa với thông tin sau:
    - Tên: {doctor.name}
    - Khu vực: {doctor.area or 'Không xác định'}
    - Học vấn: {doctor.education or 'Đại học Y khoa'}
    - Chứng chỉ/Chuyên môn: {doctor.certificate or 'Nha khoa tổng quát'}
    
    Đoạn 1: Giới thiệu chung - khoảng 3-4 câu về bác sĩ, kinh nghiệm và phong cách làm việc.
    Đoạn 2: Chuyên môn - khoảng 3-4 câu về lĩnh vực chuyên môn và kỹ năng nổi bật.
    
    Viết bằng tiếng Việt, thân thiện, chuyên nghiệp, độ dài mỗi đoạn khoảng 3-5 dòng.
    """
    
    # Gọi API Gemini
    model = genai.GenerativeModel('gemini-1.5-pro')
    response = model.generate_content(prompt)
    
    if response:
        # Tách thành 2 đoạn
        paragraphs = response.text.split('\n\n')
        if len(paragraphs) >= 2:
            return {
                'intro': paragraphs[0].replace('Đoạn 1:', '').strip(), 
                'expertise': paragraphs[1].replace('Đoạn 2:', '').strip()
            }
    
    # Fallback nếu có lỗi
    return {
        'intro': f"Bác sĩ {doctor.name} là một trong những bác sĩ tận tâm tại phòng khám PrimeCare.",
        'expertise': f"Bác sĩ {doctor.name} chuyên về chăm sóc nha khoa toàn diện, bao gồm các dịch vụ phòng ngừa, điều trị và thẩm mỹ."
    }

def doctor_detail(request, slug):
    """Hiển thị thông tin chi tiết của một bác sĩ dựa trên slug"""
    doctor = get_object_or_404(Doctor, slug=slug)
    
    # Xử lý chứng chỉ thành list
    if doctor.certificate:
        certificates = doctor.certificate.split('\n')
        certificates = [cert.strip() for cert in certificates if cert.strip()]
    else:
        certificates = []

    # Lấy danh sách các bác sĩ khác
    all_other_doctors = list(Doctor.objects.exclude(id=doctor.id))
    
    # Random 10 bác sĩ hoặc ít hơn nếu không đủ
    num_doctors = min(10, len(all_other_doctors))
    other_doctors = random.sample(all_other_doctors, num_doctors)
    
    # Dữ liệu kỹ năng giờ đây lấy trực tiếp từ model
    expertise_data = {
        'healing_therapy': doctor.healing_therapy,
        'pain_management': doctor.pain_management,
        'diagnosis': doctor.diagnosis
    }
    
    # Trả về response với context
    return render(request, 'doctors/doctor_detail.html', {
        'doctor': doctor,
        'other_doctors': other_doctors,
        'expertise_data': expertise_data,
        'expertise_intro': doctor.bio_expertise_1,
        'expertise_additional': doctor.bio_expertise_2,
        'certificates': certificates,
    })

def doctor_detail_by_id(request, doctor_id):
    """Xử lý các URL cũ dựa trên ID và chuyển hướng đến URL mới dựa trên slug"""
    doctor = get_object_or_404(Doctor, id=doctor_id)
    return redirect('doctors:detail', slug=doctor.slug)

# Các trang tĩnh
def home(request):
    return render(request, 'pages/index.html')
    
def about(request):
    return render(request, 'pages/about-VN.html')
    
def contact(request):
    return render(request, 'pages/contact.html')
    
def gallery(request):
    return render(request, 'pages/gallery.html')
    
def faqs(request):
    return render(request, 'pages/faqs.html')
    
def testimonials(request):
    return render(request, 'pages/testimonials.html')

def service(request):
    return render(request, 'services/list.html')

def terms(request):
    return render(request, 'pages/terms.html')
    
def privacy(request):
    return render(request, 'pages/privacy.html')
    
def support(request):
    return render(request, 'pages/support.html')

def price_list(request):
    return render(request, 'pages/price-list.html')

# View tạm thời cho services namespace
def service_placeholder(request):
    """View tạm thời cho dịch vụ"""
    return render(request, 'services/list.html', {
        'message': 'Các dịch vụ sẽ được cập nhật sớm!'
    })

def search_doctors(request):
    query = request.GET.get('q', '').strip()
    page = int(request.GET.get('page', 1))
    per_page = 8  # Số bác sĩ mỗi trang

    if query:
        doctors = Doctor.objects.filter(
            Q(name__icontains=query) | 
            Q(area__icontains=query) |
            Q(education__icontains=query) |
            Q(certificate__icontains=query)
        ).order_by('name')
    else:
        doctors = Doctor.objects.all().order_by('id')

    paginator = Paginator(doctors, per_page)
    page_obj = paginator.get_page(page)

    results = []
    for doctor in page_obj:
        if doctor.image:
            image_path = settings.STATIC_URL + 'images/doctor_images/' + str(doctor.image)
        else:
            image_path = settings.STATIC_URL + 'images/doctor_images/default-doctor.jpg'
        results.append({
            'id': doctor.id,
            'name': doctor.name,
            'area': doctor.area,
            'image': image_path,
            'slug': doctor.slug,
            'education': doctor.education,
            'certificate': doctor.certificate
        })
    return JsonResponse({'results': results})
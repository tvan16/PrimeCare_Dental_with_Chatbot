# PrimeCare Dental Clinic

PrimeCare Dental Clinic là một ứng dụng web quản lý phòng khám nha khoa được xây dựng bằng Django, tích hợp chatbot thông minh để hỗ trợ tương tác với bệnh nhân.

## Tính năng chính

- Quản lý thông tin bác sĩ và lịch hẹn
- Hệ thống đặt lịch hẹn trực tuyến
- Quản lý dịch vụ nha khoa
- Blog chia sẻ thông tin về sức khỏe răng miệng
- Chatbot hỗ trợ tư vấn 24/7
- Giao diện người dùng thân thiện, responsive

## Công nghệ sử dụng

- **Backend**: Django 5.0.2
- **Frontend**: HTML, CSS, JavaScript
- **Database**: SQLite
- **Các thư viện chính**:
  - Pillow: Xử lý hình ảnh
  - django-crispy-forms: Tạo form đẹp và responsive
  - django-ckeditor: Trình soạn thảo văn bản phong phú
  - django-widget-tweaks: Tùy chỉnh form widgets
  - django-cleanup: Tự động dọn dẹp file media
  - django-debug-toolbar: Công cụ debug
  - requests: Gọi API
  - python-dateutil: Xử lý ngày tháng
  - markdown: Hỗ trợ định dạng Markdown

## Cài đặt

1. Clone repository:
```bash
git clone [repository-url]
cd PrimeCare_Dental_with_Chatbot
```

2. Tạo môi trường ảo và kích hoạt:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Cài đặt các dependencies:
```bash
pip install -r requirements.txt
```

4. Chạy migrations:
```bash
python manage.py migrate
```

5. Tạo superuser (tùy chọn):
```bash
python manage.py createsuperuser
```

6. Chạy server:
```bash
python manage.py runserver
```

## Cấu trúc dự án

- `apps/`: Chứa các ứng dụng Django
  - `blogs/`: Quản lý bài viết blog
  - `services/`: Quản lý dịch vụ nha khoa
  - `chatbot/`: Xử lý tương tác với chatbot
  - `doctors/`: Quản lý thông tin bác sĩ
- `config/`: Cấu hình dự án
- `templates/`: Chứa các template HTML
- `static/`: Chứa các file tĩnh (CSS, JS, images)
- `media/`: Lưu trữ file media được upload
- `staticfiles/`: Chứa các file tĩnh đã được collect

## Đóng góp

Mọi đóng góp đều được hoan nghênh! Vui lòng tạo pull request hoặc issue để đóng góp vào dự án.

## Giấy phép

Dự án này được phát hành dưới giấy phép MIT. 
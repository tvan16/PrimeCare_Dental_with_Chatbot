# PrimeCare Dental Clinic

A modern, full-featured dental clinic management system built with Django, featuring an intelligent chatbot for enhanced patient interaction and streamlined clinic operations.

## 🌟 Key Features

- **Doctor Management**
  - Comprehensive doctor profiles and scheduling
  - Expertise and specialization tracking
  - Professional credentials and achievements

- **Appointment System**
  - Online appointment booking
  - Real-time availability checking
  - Automated appointment reminders
  - Calendar integration

- **Service Management**
  - Detailed service catalog
  - Pricing management
  - Service categories and subcategories
  - Treatment descriptions and benefits

- **Patient Portal**
  - Secure patient profiles
  - Treatment history
  - Online consultation requests
  - Document management

- **Blog Platform**
  - Dental health information sharing
  - Expert articles and tips
  - SEO-optimized content
  - Category management

- **AI-Powered Chatbot**
  - 24/7 patient support
  - Instant responses to common queries
  - Appointment scheduling assistance
  - Service information provision

- **Responsive Design**
  - Mobile-first approach
  - Cross-browser compatibility
  - Modern, intuitive interface
  - Accessibility compliance

## 🛠️ Technology Stack

### Backend
- **Framework**: Django 5.0.2
- **Database**: SQLite (Development) / PostgreSQL (Production)
- **Authentication**: Django's built-in auth system
- **API**: Django REST Framework

### Frontend
- **HTML5/CSS3**
- **JavaScript/jQuery**
- **Bootstrap 5**
- **Responsive Design**

### Key Libraries
- **Pillow**: Advanced image processing
- **django-crispy-forms**: Enhanced form rendering
- **django-ckeditor**: Rich text editing
- **django-widget-tweaks**: Form widget customization
- **django-cleanup**: Automatic media file management
- **django-debug-toolbar**: Development debugging
- **requests**: API integration
- **python-dateutil**: Date/time handling
- **markdown**: Content formatting

## 🚀 Installation

1. **Clone the Repository**
```bash
git clone https://github.com/tvan16/PrimeCare_Dental_with_Chatbot.git
cd PrimeCare_Dental_with_Chatbot
```

2. **Set Up Virtual Environment**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Environment Configuration**
```bash
# Create .env file
cp .env.example .env
# Edit .env with your configuration
```

5. **Database Setup**
```bash
python manage.py migrate
python manage.py createsuperuser
```

6. **Static Files**
```bash
python manage.py collectstatic
```

7. **Run Development Server**
```bash
python manage.py runserver
```

## 📁 Project Structure

```
PrimeCare_Dental_with_Chatbot/
├── apps/                    # Django applications
│   ├── blogs/              # Blog management
│   ├── services/           # Service management
│   ├── chatbot/            # AI chatbot integration
│   └── doctors/            # Doctor management
├── config/                 # Project configuration
├── templates/             # HTML templates
├── static/               # Static files (CSS, JS, images)
├── media/               # User-uploaded files
├── staticfiles/        # Collected static files
└── requirements.txt   # Project dependencies
```

## 🔧 Development

### Code Style
- Follow PEP 8 guidelines
- Use meaningful variable names
- Write docstrings for functions and classes
- Keep functions small and focused

### Git Workflow
1. Create feature branch
2. Make changes
3. Write tests
4. Submit pull request
5. Code review
6. Merge to main

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Your Name** - *Initial work* - [tvan16](https://github.com/tvan16)

## 🙏 Acknowledgments

- Thanks to all contributors
- Inspired by modern dental clinic needs
- Built with Django community best practices

## 📞 Support

For support, email [your-email@example.com] or open an issue in the repository. 
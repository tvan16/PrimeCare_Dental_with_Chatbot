from django.core.management.base import BaseCommand
from apps.doctors.models import Doctor
from apps.doctors.utils import vietnamese_slugify

class Command(BaseCommand):
    help = "Generate slugs for existing doctors"

    def handle(self, *args, **options):
        doctors = Doctor.objects.filter(slug__isnull=True) | Doctor.objects.filter(slug='')
        for doctor in doctors:
            # Sử dụng vietnamese_slugify thay vì slugify
            base_slug = vietnamese_slugify(doctor.name)
            slug = base_slug
            counter = 1
            
            # Kiểm tra xem slug đã tồn tại chưa
            while Doctor.objects.filter(slug=slug).exclude(id=doctor.id).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
                
            doctor.slug = slug
            doctor.save(update_fields=['slug'])  # Chỉ cập nhật trường slug
            self.stdout.write(self.style.SUCCESS(f'Created slug "{slug}" for doctor "{doctor.name}"'))
        
        self.stdout.write(self.style.SUCCESS('Successfully generated slugs for all doctors'))
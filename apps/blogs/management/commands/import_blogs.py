import json
import os
from django.core.management.base import BaseCommand
from django.core.files import File
from apps.blogs.models import Blog, Category, Tag
from django.utils.text import slugify
from django.utils import timezone
from datetime import datetime
from unidecode import unidecode

class Command(BaseCommand):
    help = 'Import blog data from JSON file and automatically add new tags'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            help='Path to JSON file containing blog data',
            default='data/news-data.json'
        )

    def handle(self, *args, **options):
        json_file = options['file']
        
        if not os.path.exists(json_file):
            self.stdout.write(
                self.style.ERROR(f'File {json_file} does not exist!')
            )
            return

        try:
            with open(json_file, encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError:
            self.stdout.write(
                self.style.ERROR(f'Invalid JSON file: {json_file}')
            )
            return

        for item in data:
            try:
                # Xử lý category
                cat_name = item.get('category', 'Khác')
                cat_slug = slugify(unidecode(cat_name))
                category, cat_created = Category.objects.get_or_create(
                    name=cat_name,
                    slug=cat_slug
                )
                if cat_created:
                    self.stdout.write(
                        self.style.SUCCESS(f'Created new category: {cat_name}')
                    )

                # Xử lý tags
                tags = []
                for tag_name in item.get('tags', []):
                    tag_slug = slugify(unidecode(tag_name))
                    tag, tag_created = Tag.objects.get_or_create(
                        name=tag_name,
                        slug=tag_slug
                    )
                    tags.append(tag)
                    if tag_created:
                        self.stdout.write(
                            self.style.SUCCESS(f'Created new tag: {tag_name}')
                        )

                # Tạo slug cho blog
                title = item['title']
                slug = slugify(unidecode(title))

                # Xử lý thời gian
                publish_time = item.get('publish_time')
                if publish_time:
                    try:
                        publish_time = datetime.strptime(publish_time, '%Y-%m-%d')
                    except ValueError:
                        self.stdout.write(
                            self.style.WARNING(
                                f'Invalid date format for {title}, using current time'
                            )
                        )
                        publish_time = timezone.now()
                else:
                    publish_time = timezone.now()

                # Xử lý ảnh
                image_path = item.get('image')
                if image_path and os.path.exists(f'static/images/{image_path}'):
                    with open(f'static/images/{image_path}', 'rb') as img_file:
                        image_file = File(img_file)
                        # Tạo hoặc cập nhật blog
                        blog, created = Blog.objects.update_or_create(
                            slug=slug,
                            defaults={
                                'name': title,
                                'category': category,
                                'image': image_file,
                                'intro': item.get('intro', ''),
                                'detail_content_1': item.get('detail_content_1', ''),
                                'detail_content_2': item.get('detail_content_2', ''),
                                'quote': item.get('quote', ''),
                                'detail_content_3': item.get('detail_content_3', ''),
                                'title': item.get('title', ''),
                                'detail_content_4': item.get('detail_content_4', ''),
                                'detail_content_5': item.get('detail_content_5', ''),
                                'publish_time': publish_time,
                            }
                        )
                else:
                    # Tạo hoặc cập nhật blog không có ảnh
                    blog, created = Blog.objects.update_or_create(
                        slug=slug,
                        defaults={
                            'name': title,
                            'category': category,
                            'intro': item.get('intro', ''),
                            'detail_content_1': item.get('detail_content_1', ''),
                            'detail_content_2': item.get('detail_content_2', ''),
                            'quote': item.get('quote', ''),
                            'detail_content_3': item.get('detail_content_3', ''),
                            'title': item.get('title', ''),
                            'detail_content_4': item.get('detail_content_4', ''),
                            'detail_content_5': item.get('detail_content_5', ''),
                            'publish_time': publish_time,
                        }
                    )

                # Thêm tags cho blog
                blog.tags.set(tags)

                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f'Successfully created blog: {title}')
                    )
                else:
                    self.stdout.write(
                        self.style.SUCCESS(f'Successfully updated blog: {title}')
                    )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error processing blog {title}: {str(e)}')
                )
                continue

        self.stdout.write(
            self.style.SUCCESS('Successfully completed blog import!')
        ) 
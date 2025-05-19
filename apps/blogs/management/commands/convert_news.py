import json
import os
from datetime import datetime
from django.core.management.base import BaseCommand

# Từ khóa nhận diện category/tags
CATEGORY_KEYWORDS = [
    ("Niềng răng", ["niềng răng", "chỉnh nha"]),
    ("Trồng răng Implant", ["implant", "trồng răng implant"]),
    ("Nha khoa trẻ em", ["trẻ em", "nhi đồng", "răng sữa"]),
    ("Nha khoa thẩm mỹ", ["thẩm mỹ", "làm đẹp", "tẩy trắng", "dán sứ"]),
    ("Nha khoa phục hồi", ["phục hồi", "trám răng", "bọc răng", "phục hình"]),
    ("Nha khoa tổng quát", ["tổng quát", "chung", "khám răng", "sâu răng", "viêm nướu", "chăm sóc răng miệng"]),
]

TAG_KEYWORDS = [
    ("Niềng răng", ["niềng răng", "chỉnh nha"]),
    ("Implant", ["implant", "trồng răng implant"]),
    ("Trẻ em", ["trẻ em", "nhi đồng", "răng sữa"]),
    ("Thẩm mỹ", ["thẩm mỹ", "làm đẹp", "tẩy trắng", "dán sứ"]),
    ("Phục hồi", ["phục hồi", "trám răng", "bọc răng", "phục hình"]),
    ("Tổng quát", ["tổng quát", "chung", "khám răng", "sâu răng", "viêm nướu", "chăm sóc răng miệng"]),
    ("Kiến thức nha khoa", ["kiến thức", "hướng dẫn", "mẹo", "lời khuyên"]),
]

def detect_category_and_tags(title, content):
    text = f"{title} {content}".lower()
    # Category
    for cat, keywords in CATEGORY_KEYWORDS:
        if any(kw in text for kw in keywords):
            category = cat
            break
    else:
        category = "Nha khoa tổng quát"
    # Tags
    tags = set()
    for tag, keywords in TAG_KEYWORDS:
        if any(kw in text for kw in keywords):
            tags.add(tag)
    if not tags:
        tags.add("Kiến thức nha khoa")
    return category, list(tags)

class Command(BaseCommand):
    help = 'Convert news from news-detail.json to news-data.json format, tự động nhận diện category/tags.'

    def handle(self, *args, **options):
        try:
            with open('data/news-detail.json', 'r', encoding='utf-8') as f:
                detail_data = json.load(f)
            with open('data/news-data.json', 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
            converted_data = []
            for idx, item in enumerate(detail_data[:3]):
                title = item.get('title', '')
                content = item.get('content', '')
                subtitle = item.get('subtitle', '')
                category, tags = detect_category_and_tags(title, content)
                content_parts = [part.strip() for part in content.split('\n\n') if part.strip()]
                # Tách các phần nội dung
                intro = content_parts[0] if len(content_parts) > 0 else ''
                detail_content_1 = content_parts[1] if len(content_parts) > 1 else ''
                detail_content_2 = content_parts[2] if len(content_parts) > 2 else ''
                quote = content_parts[3] if len(content_parts) > 3 else ''
                detail_content_3 = content_parts[4] if len(content_parts) > 4 else ''
                detail_content_4 = content_parts[5] if len(content_parts) > 5 else ''
                detail_content_5 = content_parts[6] if len(content_parts) > 6 else ''
                # Để trống trường ảnh
                image = ""
                # Ngày đăng
                publish_time = datetime.now().strftime('%Y-%m-%d')
                # Tạo blog dict
                new_blog = {
                    "title": title,
                    "category": category,
                    "tags": tags,
                    "image": image,
                    "intro": intro,
                    "detail_content_1": detail_content_1,
                    "detail_content_2": detail_content_2,
                    "quote": quote,
                    "detail_content_3": detail_content_3,
                    "detail_content_4": detail_content_4,
                    "detail_content_5": detail_content_5,
                    "publish_time": publish_time
                }
                converted_data.append(new_blog)
            # Nối vào file news-data.json
            combined_data = existing_data + converted_data
            with open('data/news-data.json', 'w', encoding='utf-8') as f:
                json.dump(combined_data, f, ensure_ascii=False, indent=4)
            self.stdout.write(self.style.SUCCESS(f'Đã chuyển đổi và thêm {len(converted_data)} bài blog mới vào news-data.json'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}'))

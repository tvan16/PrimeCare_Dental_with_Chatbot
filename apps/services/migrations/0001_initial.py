# Generated by Django 5.2 on 2025-05-09 14:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MainService',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(unique=True)),
                ('intro', models.TextField(blank=True, verbose_name='Giới thiệu chung')),
                ('image', models.ImageField(blank=True, null=True, upload_to='main_service_images/')),
                ('benefits_title', models.CharField(default='Các Lợi Ích Chính', max_length=255)),
                ('benefits_intro', models.TextField(blank=True, verbose_name='Đoạn giới thiệu lợi ích')),
                ('benefits_list', models.TextField(blank=True, verbose_name='Danh sách lợi ích (mỗi dòng 1 lợi ích)')),
                ('benefits_outro', models.TextField(blank=True, verbose_name='Đoạn kết lợi ích')),
                ('faq_title', models.CharField(default='Mọi điều bạn cần biết', max_length=255)),
                ('faq_subtitle', models.CharField(blank=True, default='', max_length=255)),
                ('faq_question_1', models.CharField(blank=True, max_length=255)),
                ('faq_answer_1', models.TextField(blank=True)),
                ('faq_question_2', models.CharField(blank=True, max_length=255)),
                ('faq_answer_2', models.TextField(blank=True)),
                ('faq_question_3', models.CharField(blank=True, max_length=255)),
                ('faq_answer_3', models.TextField(blank=True)),
                ('faq_question_4', models.CharField(blank=True, max_length=255)),
                ('faq_answer_4', models.TextField(blank=True)),
                ('faq_question_5', models.CharField(blank=True, max_length=255)),
                ('faq_answer_5', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='SubService',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('slug', models.SlugField(unique=True)),
                ('original_price', models.DecimalField(decimal_places=0, max_digits=12)),
                ('discount_price', models.DecimalField(blank=True, decimal_places=0, max_digits=12, null=True)),
                ('discount_percent', models.PositiveIntegerField(default=0)),
                ('description', models.TextField(blank=True)),
                ('main_service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sub_services', to='services.mainservice')),
            ],
        ),
        migrations.CreateModel(
            name='ServiceImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='service_images/')),
                ('is_primary', models.BooleanField(default=False)),
                ('sub_service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='services.subservice')),
            ],
        ),
    ]

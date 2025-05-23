# Generated by Django 5.2 on 2025-04-30 19:56

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Doctor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Họ và tên')),
                ('area', models.CharField(max_length=200, verbose_name='Chuyên khoa')),
                ('education', models.TextField(verbose_name='Quá trình đào tạo')),
                ('certificate', models.TextField(verbose_name='Chứng chỉ')),
                ('image', models.CharField(max_length=255, verbose_name='Hình ảnh')),
                ('facebook', models.URLField(blank=True, null=True)),
                ('instagram', models.URLField(blank=True, null=True)),
                ('twitter', models.URLField(blank=True, null=True, verbose_name='X (Twitter)')),
                ('bio_intro', models.TextField(blank=True, null=True)),
                ('bio_expertise', models.TextField(blank=True, null=True)),
                ('bio_generated_at', models.DateTimeField(blank=True, null=True)),
            ],
        ),
    ]

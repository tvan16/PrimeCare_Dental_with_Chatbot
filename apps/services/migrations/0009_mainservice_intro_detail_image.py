# Generated by Django 5.2 on 2025-05-10 03:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0008_rename_image_mainservice_benefits_image_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='mainservice',
            name='intro_detail_image',
            field=models.ImageField(blank=True, null=True, upload_to='main_service_images/'),
        ),
    ]

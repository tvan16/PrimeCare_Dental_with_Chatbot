# Generated by Django 5.2 on 2025-05-10 02:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0005_mainservice_detail_content'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='subservice',
            name='discount_price',
        ),
        migrations.RemoveField(
            model_name='subservice',
            name='original_price',
        ),
        migrations.AddField(
            model_name='subservice',
            name='discount_price_max',
            field=models.DecimalField(blank=True, decimal_places=0, default=0, max_digits=12, null=True),
        ),
        migrations.AddField(
            model_name='subservice',
            name='discount_price_min',
            field=models.DecimalField(blank=True, decimal_places=0, default=0, max_digits=12, null=True),
        ),
        migrations.AddField(
            model_name='subservice',
            name='original_price_max',
            field=models.DecimalField(decimal_places=0, default=0, max_digits=12),
        ),
        migrations.AddField(
            model_name='subservice',
            name='original_price_min',
            field=models.DecimalField(decimal_places=0, default=0, max_digits=12),
        ),
    ]

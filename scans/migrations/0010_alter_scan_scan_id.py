# Generated by Django 3.2.12 on 2022-12-29 18:44

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('scans', '0009_scan_tracking'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scan',
            name='scan_id',
            field=models.UUIDField(default=uuid.uuid4),
        ),
    ]

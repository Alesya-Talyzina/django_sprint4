# Generated by Django 3.2.16 on 2024-05-24 13:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0003_auto_20240523_1431'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Comment',
        ),
    ]

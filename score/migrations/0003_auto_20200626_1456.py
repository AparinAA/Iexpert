# Generated by Django 3.0.7 on 2020-06-26 11:56

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('score', '0002_expertscore'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ExpertScore',
            new_name='CheckExpertScore',
        ),
    ]

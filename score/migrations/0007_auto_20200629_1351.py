# Generated by Django 3.0.7 on 2020-06-29 10:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('score', '0006_delete_checkexpertscore'),
    ]

    operations = [
        migrations.AddField(
            model_name='scorecommon',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='Готово'),
        ),
        migrations.AddField(
            model_name='scoreexpert',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='Готово'),
        ),
    ]

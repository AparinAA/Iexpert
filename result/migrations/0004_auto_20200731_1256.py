# Generated by Django 3.0.7 on 2020-07-31 09:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('result', '0003_auto_20200730_1605'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resultmaster',
            name='status',
            field=models.CharField(choices=[('b', 'Начальный статус'), ('r', 'Может смотреть распределение'), ('w', 'Может писать комментарии')], default='b', max_length=2, verbose_name='Статус доступа'),
        ),
    ]

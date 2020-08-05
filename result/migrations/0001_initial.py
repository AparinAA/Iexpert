# Generated by Django 3.0.7 on 2020-07-31 13:27

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CheckExpertScore',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('check_exp', models.BooleanField(default=False, verbose_name='Готовность Эксперта')),
                ('count_all', models.IntegerField(default=0, verbose_name='Кол-во назначенных заявок')),
                ('count_ok', models.IntegerField(default=0, verbose_name='Кол-во готовых заявок')),
                ('date_last', models.DateField(blank=True, default=None, null=True, verbose_name='Последнее обновление')),
                ('comment', models.TextField(blank=True, max_length=2000, null=True, verbose_name='Комметарий по эксперту')),
            ],
            options={
                'verbose_name': 'Готовность оценок по эксперту',
                'verbose_name_plural': 'Готовность оценок по эксперту',
            },
        ),
        migrations.CreateModel(
            name='ResultMaster',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('b', 'Начальный статус'), ('r', 'Может смотреть распределение'), ('w', 'Может писать комментарии')], default='b', max_length=2, verbose_name='Статус доступа')),
                ('check', models.BooleanField(default=False, verbose_name='Готовность ответственного секретаря')),
                ('count_all', models.IntegerField(default=0, verbose_name='Кол-во всего заявок')),
                ('count_ok', models.IntegerField(default=0, verbose_name='Кол-во готовых комментариев')),
                ('date_last', models.DateField(blank=True, default=None, null=True, verbose_name='Последнее обновление')),
                ('comment', models.TextField(blank=True, max_length=2000, null=True, verbose_name='Любое примичание')),
            ],
            options={
                'verbose_name': 'Готовность ответственных секретарей',
                'verbose_name_plural': 'Готовность ответственных секретарей',
            },
        ),
    ]
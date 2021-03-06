# Generated by Django 3.0.7 on 2020-07-31 13:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Application',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('link_archiv', models.URLField(blank=True, verbose_name='Ссылка на архив')),
            ],
            options={
                'verbose_name': 'Заявка',
                'verbose_name_plural': 'Заявки',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Direction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Название направления')),
            ],
            options={
                'verbose_name': 'Направление',
                'verbose_name_plural': 'Направления',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='RelationExpertApplication',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('common_commission', models.BooleanField(default=False, verbose_name='Общая комиссия')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активное распределение')),
                ('application', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='rel_exp_app', to='app.Application', verbose_name='Заявка')),
            ],
            options={
                'verbose_name': 'Связь эксперта с заявкой',
                'verbose_name_plural': 'Связи экспертов и заявок',
            },
        ),
    ]

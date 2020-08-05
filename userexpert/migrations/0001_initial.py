# Generated by Django 3.0.7 on 2020-07-31 13:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
        ('info', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Expert',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('login', models.CharField(max_length=100, unique=True, verbose_name='Логин пользователя')),
                ('email', models.EmailField(max_length=255, verbose_name='Электронная почта')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активная запись')),
                ('is_admin', models.BooleanField(default=False, verbose_name='Админ')),
                ('first_name', models.CharField(max_length=100, verbose_name='Имя')),
                ('middle_name', models.CharField(max_length=100, verbose_name='Отчество')),
                ('last_name', models.CharField(max_length=100, verbose_name='Фамилия')),
                ('date_joined', models.DateField(verbose_name='Дата регистрации')),
                ('position', models.CharField(max_length=200, verbose_name='Должность')),
                ('phone', models.CharField(blank=True, max_length=200, null=True, verbose_name='Телефон')),
                ('common_commission', models.BooleanField(default=False, verbose_name='Общая комиссия')),
                ('master_group', models.BooleanField(default=False, verbose_name='Ответственный секретарь')),
                ('gender', models.CharField(choices=[('m', 'Муж'), ('f', 'Жен')], default='m', max_length=2, verbose_name='Пол')),
                ('comment', models.TextField(blank=True, default='', null=True, verbose_name='Примичание/Комментарий')),
                ('company', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='info.Company', verbose_name='Вуз/Организация')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'Эксперт',
                'verbose_name_plural': 'Эксперты',
                'ordering': ['id', 'last_name', 'first_name', 'middle_name'],
            },
        ),
        migrations.CreateModel(
            name='CustomGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('common_commission', models.BooleanField(default=False, verbose_name='Общая комиссия')),
                ('admin_group', models.BooleanField(default=False, verbose_name='Группа администраторов')),
                ('group', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='auth.Group')),
                ('master', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='Ответственный секретарь')),
            ],
            options={
                'verbose_name': 'Комиссия',
                'verbose_name_plural': 'Комиссии',
            },
        ),
    ]
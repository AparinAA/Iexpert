from datetime import datetime
from sys import path
import io
import os
from xlsxwriter import Workbook

import patterns as patterns
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from xlsxwriter import Workbook

from expert.func_export import export_personal_info_request

from expert.func_load_expert import func_load_expert
from userexpert.models import Expert, CustomGroup

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import User, Permission, PermissionsMixin
import pandas as pd
from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField, PasswordResetForm
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.http import HttpResponseRedirect
from django.urls import path, re_path
from django.shortcuts import render
import pyperclip
import clipboard

class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Повторите пароль', widget=forms.PasswordInput)

    class Meta:
        model = Expert
        fields = ('login',)

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Пароли не совпадают")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.date_joined = datetime.now(tz=None)
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = Expert
        fields = ('login', 'password', 'is_active', 'is_admin')

    def clean_password(self):
        return self.initial["password"]


from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    list_per_page = 15

    list_display = (
        'id', 'login', 'last_name', 'first_name', 'middle_name', 'is_active', 'is_admin',
        'common_commission', 'master_group', 'last_login')
    list_display_links = ('login',)
    list_filter = ['common_commission', 'is_admin', 'master_group']
    fieldsets = (
        (None, {'fields': (('login', 'password'),)}),
        ('Контактная информация', {'fields': (('email', 'phone'),)}),
        ('Персональные данные', {'fields': (('last_name', 'first_name', 'middle_name'),
                                            ('company', 'position'
                                             ),)}),
        ('Доступ', {'fields': ('is_admin', 'is_active',)}),
        ('Права', {'fields': ('user_permissions',)}),
        ('Группы', {'fields': ('groups',)}),
        ('Комментарий', {'fields': ('comment', )})

    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('login', 'password1', 'password2'),
        }),
    )
    search_fields = ('login', 'last_name', 'first_name', 'middle_name',)
    ordering = ('login',)
    filter_horizontal = [
        'user_permissions',
        'groups']
    change_list_template = "admin/model_user.html"
    change_form_template = 'admin/change_form_custom.html'

    def my_reset_password(self, request, user_id):
        user = get_object_or_404(self.model, pk=user_id)
        new_password = BaseUserManager().make_random_password(length=8)
        user.set_password(new_password)
        user.save()
        self.message_user(request, "Новый пароль скопирован в буфер обмена: {}".format(new_password))
        return HttpResponseRedirect("../")

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('generate_users/', self.generate_users),
            path('update_users/', self.update_users),
            path('load_users/', self.load_users),
            path('export_users/', self.export_users),

            path('<int:user_id>/my_reset_password/', self.my_reset_password, name='my_reset_password')
        ]
        return my_urls + urls

    def update_users(self, request):
        for user in self.model.objects.all():
            try:
                user.save()
            except:
                pass
        self.message_user(request, "Все пользователи обновлены")
        return HttpResponseRedirect("../")


    def load_users(self, request):
        #self.message_user(request, "Допустим загрузили экспертов")
        #return HttpResponseRedirect("../")
        return func_load_expert(request)

    def export_users(self, request):
        # self.message_user(request, "Допустим выгрузили экспертов")
        return export_personal_info_request(request)

    def generate_login_and_password(self, request, data, head=['login', 'password']):
        output = io.BytesIO()

        workbook = Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet()
        for col_num in range(len(head)):
            worksheet.write(0, col_num, head[col_num])

        for row_num, columns in enumerate(data.values):
            for col_num, cell_data in enumerate(columns):
                worksheet.write(row_num + 1, col_num, cell_data)
        workbook.close()
        date_ = '{}-{} {}-{}-{}'.format(datetime.now().hour, datetime.now().minute,
                                        datetime.now().day, datetime.now().month, datetime.now().year)
        output.seek(0)
        response = HttpResponse(output.read(),
                                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response['Content-Disposition'] = "attachment; filename=generate_login_{}.xlsx".format(date_)
        output.close()
        return response

    def generate_users(self, request):

        def sub_generate(self, count, osnova):
            def generate(first_num, count, osnova, logins=set()):
                ar = []
                i = 0
                while i < count:
                    log = '{}{}'.format(osnova, first_num + i)
                    if log not in logins:
                        ar.append([log, BaseUserManager().make_random_password(length=8)])
                    i += 1
                return pd.DataFrame(ar, columns=['login', 'password'])

            set_login = set()
            for val in self.model.objects.all().values('login'):
                set_login.add(val['login'])
            last_number = 1
            while '{}{}'.format(osnova, last_number) in set_login:
                last_number += 1
            data = generate(last_number, count, osnova)
            return data
        
        #кнопка вернуться
        if 'prev' in request.POST:
            return HttpResponseRedirect('../')

        #перейти на страницу для генерации
        elif 'generate' in request.POST:
            count = int(1)
            osnova = "example"
            data = sub_generate(self, count, osnova)
            return render(request, 'admin/generate_users.html',
                          {'list': data['login'].tolist(), 'id_number' : count, 'id_nameOs' : osnova,
                           'title': u'Генерация логинов и паролей',})

        # Генерируем новые логины
        elif 'sgen' in request.POST:
            count = int(request.POST.get('num'))
            osnova = str(request.POST.get('name'))
            data = sub_generate(self, count, osnova)
            return render(request, 'admin/generate_users.html',
                          {'list': data['login'].tolist(), 'id_number' : count, 'id_nameOs' : osnova,
                           'title': u'Генерация логинов и паролей',})

        # Если нажали подтвердить, то все, сохраняем и экспортируем xlsx
        elif 'apply' in request.POST:
            count = int(request.POST.get('number'))
            osnova = str(request.POST.get('nameOs'))
            data = sub_generate(self, count, osnova)
            self.message_user(request, "Сгенерировано новых логинов: {}".format(count))
            for login, password in data[['login','password']].values:
                exp = Expert.objects.create_user(login, password=password)
                # exp.save()

            return self.generate_login_and_password(request, data) #


from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import Group


class GroupInline(admin.StackedInline):
    model = CustomGroup
    can_delete = False
    verbose_name_plural = 'custom groups'


class GroupAdmin(BaseGroupAdmin):
    inlines = (GroupInline,)
    list_display = ['id', 'name', ]
    list_per_page = 15

    list_display_links = ('name',)
    fields = ['name', 'permissions']

    class Meta:
        model = Group


admin.site.register(Expert, UserAdmin)
admin.site.unregister(Group)
# admin.site.register(Group, GroupAdmin)
from django.forms import ModelForm


class CustomGroupForm(ModelForm):
    name = forms.CharField(max_length=256)
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = CustomGroup
        fields = ('name',
                  'permissions',
                  )

    def __init__(self, *args, **kwargs):
        super(CustomGroupForm, self).__init__(*args, **kwargs)
        try:
            self.fields['name'].initial = self.instance.name()
            self.fields['permissions'].initial = self.instance.permissions()
        except:
            pass

    def save(self, *args, **kwargs):
        if 'instance' in self:
            group = self.instance.group
            group.name = self.cleaned_data.get('name')
            group.common_commission = self.cleaned_data.get('common_commission')
            group.admin_group = self.cleaned_data.get('admin_group')
            group.master = self.cleaned_data.get('master')
            group.permissions.clear()
            for per in self.cleaned_data.get('permissions'):
                group.permissions.add(per)

            group.save()
            return group
        else:
            super(CustomGroupForm, self).save(commit=False)
            group_name = self.cleaned_data.get('name')
            group, _ = Group.objects.get_or_create(name=group_name)
            for per in self.cleaned_data.get('permissions'):
                group.permissions.add(per)
            group.save()

            cg, _ = CustomGroup.objects.get_or_create(group=group)
            cg.common_commission = self.cleaned_data.get('common_commission')
            cg.admin_group = self.cleaned_data.get('admin_group')
            cg.master = self.cleaned_data.get('master')
            cg.save()
            return cg


@admin.register(CustomGroup)
class CustomGroupAdmin(admin.ModelAdmin):
    form = CustomGroupForm

    list_per_page = 15
    list_display = ['id', 'group', 'common_commission', 'admin_group']
    list_display_links = ['group']
    # list_display_links = ('name',)
    list_filter = ['common_commission', 'admin_group']
    fields = ['name', 'master', 'common_commission', 'admin_group',
              'permissions'
              ]

    # filter_horizontal = ['permissions']

    class Meta:
        model = CustomGroup

    # fields = ['name', 'permissions', 'email_alias']

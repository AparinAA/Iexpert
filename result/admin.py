import datetime

from django.contrib import admin

# Register your models here.
from django.http import HttpResponseRedirect, HttpResponse

from app.models import Application
from result.models import CheckExpertScore, CheckGroups, CheckApplication
from score.admin import MyScoreBaseAdmin
from userexpert.models import Expert, CustomGroup
from django.http import HttpResponseRedirect
from django.urls import path
import io
import os
from xlsxwriter import Workbook
import pandas as pd
from datetime import datetime
from .function_upload import upload_expert, upload_group, upload_app

@admin.register(CheckExpertScore)
class ExpertScoreAdmin(MyScoreBaseAdmin):
    list_per_page = 15
    list_display = ('id', 'expert', 'check_exp', 'count_ok', 'count_all', 'date_last')
    list_display_links = ('expert',)
    list_filter = ('check_exp', )
    fieldsets = (
        (None, {'fields': ('check_exp', 'comment')}),
        # ('Эксперты', {'fields': ('experts', )})
    )
    search_fields = ['expert__first_name', 'expert__second_name', 'expert__last_name', ]
    ordering = ('expert',)
    change_form_template = 'admin/change_expert_score_admin.html'

    def load_from_relation(self, request):
        """
        Проверяем есть ли связи в общей комиссии, которые мы ещё не добавили, если есть, добавляем
        """
        count = upload_expert()
        if count:
            log = "Объекты добавлены в количестве {} шт".format(count)
        else:
            log = "Нет объектов для добавления".format(count)
        return log



# @admin.register(CheckGroups)
class CheckGroupsAdmin(MyScoreBaseAdmin):
    list_per_page = 15
    list_display = ('id', 'commission', 'check_group', 'count_exp_ok',
                    'count_exp_all', 'count_app_ok', 'count_app_all', 'date_last')
    list_display_links = ('commission',)
    list_filter = ('commission',)
    fieldsets = (
        (None, {'fields': ('check_group', 'comment')}),
    )
    ordering = ('commission',)
    change_form_template = 'admin/change_result_all.html'

    #change_list_template = "admin/result_all.html"

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('load_from_relation/', self.load_from_relation),
            path('reload_scores/', self.reload_scores)
        ]
        return my_urls + urls

    def export_itog(self, request):
        self.message_user(request, "ТУТ БУДЕТ КАСТОМНЫЙ ЭКСПОРТ")  # TODO EXPORT
        return response


    def load_from_relation(self, request): # TODO Не работает. Исправить
        """
        Проверяем есть ли связи в общей комиссии, которые мы ещё не добавили, если есть, добавляем
        """
        count = upload_group()
        if count:
            log = "Объекты добавлены в количестве {} шт".format(count)
        else:
            log = "Нет объектов для добавления".format(count)
        return log




# @admin.register(CheckApplication)
class CheckApplicationAdmin(MyScoreBaseAdmin):
    list_per_page = 15
    list_display = ('id', 'application', 'check_app', 'count_exp_ok', 'count_exp_all', 'date_last')
    list_display_links = ('application',)
    list_filter = ('check_app', )
    fieldsets = (
        (None, {'fields': ('check_app', 'comment')}),
    )
    ordering = ('application',)
    change_form_template = 'admin/change_check_application_admin.html'

    def load_from_relation(self, request):
        """
        Проверяем есть ли связи в общей комиссии, которые мы ещё не добавили, если есть, добавляем
        """
        count = upload_app()
        if count:
            log = "Объекты добавлены в количестве {} шт".format(count)
        else:
            log = "Нет объектов для добавления".format(count)
        return log

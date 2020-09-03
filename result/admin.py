import datetime

from django.contrib import admin

# Register your models here.
from django.http import HttpResponseRedirect, HttpResponse

from app.models import Application
from result.models import CheckExpertScore, ResultMaster
from score.admin import MyScoreBaseAdmin
from userexpert.models import Expert, CustomGroup
from django.http import HttpResponseRedirect
from django.urls import path
import io
import os
from xlsxwriter import Workbook
import pandas as pd
from datetime import datetime
from .function_upload import upload_expert, upload_master


@admin.register(CheckExpertScore)
class ExpertScoreAdmin(MyScoreBaseAdmin):
    list_per_page = 15
    list_display = ('id', 'expert', 'check_exp', 'count_ok', 'count_all', 'date_last')
    list_display_links = ('expert',)
    list_filter = ('check_exp',)
    fieldsets = (
        (None, {'fields': ('check_exp',
                           # 'comment'
                           )}),
        # ('Эксперты', {'fields': ('experts', )})
    )
    search_fields = ['expert__first_name', ]
    ordering = ('expert__last_name',)
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


@admin.register(ResultMaster)
class ResultMasterAdmin(MyScoreBaseAdmin):
    list_per_page = 15
    list_display = ('id', 'master', 'status', 'check', 'count_ok', 'count_all', 'date_last')
    list_display_links = ('master',)
    list_filter = ('status', 'check',)
    fieldsets = (
        (None, {'fields': ('status', 'check',
                           )}),
        ('Примичание', {'fields': ('comment',
                                   )}),
    )
    search_fields = ['master__first_name', 'master__second_name', 'master__last_name', ]
    ordering = ('master__first_name',)
    change_form_template = 'admin/change_result_master.html'

    def load_from_relation(self, request):
        """
        Проверяем есть ли связи в общей комиссии, которые мы ещё не добавили, если есть, добавляем
        """
        count = upload_master()
        if count:
            log = "Объекты добавлены в количестве {} шт".format(count)
        else:
            log = "Нет объектов для добавления".format(count)
        return log

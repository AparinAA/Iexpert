from django.contrib import admin
from django.forms import Textarea
from django.http import HttpResponseRedirect
from django.urls import path

from app.models import Application, RelationExpertApplication
from import_export.admin import ImportExportActionModelAdmin
from score.models import ScoreCommon, ScoreExpert, ScoreAll, ScoreCommonAll, ScoreExpertAll
from .function_upload import upload_score_common, upload_score_expert, upload_score_all
from expert.fuction_for_all import reload_scores

from django.db import models

class MyScoreBaseAdmin(ImportExportActionModelAdmin):
    change_list_template = "admin/model_change_list.html"
    formfield_overrides = {
        models.TextField: {'widget': Textarea(
            attrs={'rows': 3,
                   'cols': 70})},
    }

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('load_from_relation/', self.load_from_relation),
            path('reload_scores/', self.reload_scores)
        ]
        return my_urls + urls

    def load_from_relation(self, request):
        return 'Ничего не произошло'

    def reload_scores(self, request):
        log = self.load_from_relation(request)
        reload_scores(self.model)
        self.message_user(request, "Оценки обновились и " + log)
        return HttpResponseRedirect("../")


@admin.register(ScoreCommon)
class ScoreCommonCommissionAdmin(MyScoreBaseAdmin):

    list_per_page = 15
    list_display = ('id', 'relation_exp_app', 'is_active', 'check', 'score', 'date_last')
    list_display_links = ('relation_exp_app',)
    list_filter = ('check',)
    fieldsets = (
        (None, {'fields': ('score', 'comment',)}),
        # ('Эксперты', {'fields': ('experts', )})
    )
    search_fields = ['score'
        #'relation_exp_app__expert',
                  #   'relation_exp_app__expert__middle_name',
                  #   'relation_exp_app__expert__first_name',
                  #   'relation_exp_app__application__name__name',
                  #   'relation_exp_app__application__vuz__short_name',
                  #   'relation_exp_app__application__vuz__full_name',
                  #   'check',
                     #
                     ]
    ordering = ('relation_exp_app',)
    change_form_template = 'admin/score_one_admin.html'

    def load_from_relation(self, request):
        count = upload_score_common()
        if count:
            log = "Объекты добавлены в количестве {} шт".format(count)
        else:
            log = "Нет объектов для добавления".format(count)
        return log


@admin.register(ScoreExpert)
class ScoreExpertCommissionAdmin(MyScoreBaseAdmin):
    list_per_page = 15
    list_display = ('id', 'relation_exp_app', 'is_active', 'check', 'score',
                    'score1', 'score2', 'score3', 'score4', 'score5', 'date_last')
    list_display_links = ('relation_exp_app',)
    list_filter = ('check',)
    fieldsets = (
        (None, {'fields': ('score1', 'score2', 'score3', 'score4', 'score5', 'comment',)}),
        # ('Эксперты', {'fields': ('experts', )})
    )
    search_fields = ['relation_exp_app', 'check', ]
    ordering = ('relation_exp_app',)
    change_form_template = 'admin/score_one_admin.html'

    def load_from_relation(self, request):
        """
        Проверяем есть ли связи в общей комиссии, которые мы ещё не добавили, если есть, добавляем
        """
        count = upload_score_expert()
        if count:
            log = "Объекты добавлены в количестве {} шт".format(count)
        else:
            log = "Нет объектов для добавления".format(count)
        return log


@admin.register(ScoreCommonAll)
class ScoreAllCommonCommissionAdmin(MyScoreBaseAdmin):
    list_per_page = 15
    list_display = ('id', 'application', 'check', 'score', 'date_last')
    list_display_links = ('application',)
    list_filter = ('application',)
    fieldsets = (
        (None, {'fields': ('comment_master',)}),
    )
    search_fields = ['application__name__name', ]
    ordering = ('application',)
    change_form_template = 'admin/score_all_admin.html'

    def load_from_relation(self, request):
        """
        Проверяем есть ли ещё заявки, которые мы ещё не добавили, если есть, добавляем
        """
        count = upload_score_all(ScoreCommonAll)
        if count:
            log = "Объекты добавлены в количестве {} шт".format(count)
        else:
            log = "Нет объектов для добавления".format(count)
        return log


@admin.register(ScoreExpertAll)
class ScoreAllExpertCommissionAdmin(MyScoreBaseAdmin):
    list_per_page = 15
    list_display = ('id', 'application', 'check', 'score',
                    'score1', 'score2', 'score3', 'score4', 'score5', 'date_last')
    list_display_links = ('application',)
    list_filter = ('application',)
    fieldsets = (
        (None, {'fields': ('comment_master',)}),
    )
    search_fields = ['application__name__name', ]
    ordering = ('application',)
    change_form_template = 'admin/score_all_admin.html'

    def load_from_relation(self, request):
        """
        Проверяем есть ли ещё заявки, которые мы ещё не добавили, если есть, добавляем
        """
        count = upload_score_all(ScoreExpertAll)
        if count:
            log = "Объекты добавлены в количестве {} шт".format(count)
        else:
            log = "Нет объектов для добавления".format(count)
        return log


@admin.register(ScoreAll)
class ScoreAllAdmin(MyScoreBaseAdmin):
    list_per_page = 15
    list_display = ('id', 'application', 'score_com', 'score_exp', 'score_final', 'date_last')
    list_display_links = ('application',)
    list_filter = ('application',)
    fields = ('application',)
    search_fields = ['application__name__name', ]
    ordering = ('application',)
    change_form_template = 'admin/score_all_admin.html'

    def load_from_relation(self, request):
        """
        Проверяем есть ли ещё заявки, которые мы ещё не добавили, если есть, добавляем
        """
        count = upload_score_all(ScoreAll)
        if count:
            log = "Объекты добавлены в количестве {} шт".format(count)
        else:
            log = "Нет объектов для добавления".format(count)
        return log

from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import path

from app.models import Application, RelationExpertApplication
from import_export.admin import ImportExportActionModelAdmin
from score.models import ScoreCommon, ScoreExpert, ScoreAll, ScoreCommonAll, ScoreExpertAll


class MyScoreBaseAdmin(ImportExportActionModelAdmin):
    change_list_template = "admin/model_change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('load_from_relation/', self.load_from_relation),
            path('export_custom/', self.export_custom),
            path('reload_scores/', self.reload_scores)
        ]
        return my_urls + urls

    def export_custom(self, request):
        self.message_user(request, "ТУТ БУДЕТ КАСТОМНЫЙ ЭКСПОРТ")  # TODO EXPORT
        return HttpResponseRedirect("../")

    def reload_scores(self, request):
        for mod in self.model.objects.all():
            mod.save()

        self.message_user(request, "Оценки обновились")

        return HttpResponseRedirect("../")

    def load_from_relation(self, request):
        self.message_user(request, "Ничего не произошло")
        return HttpResponseRedirect("../")


@admin.register(ScoreCommon)
class ScoreCommonCommissionAdmin(MyScoreBaseAdmin):
    list_per_page = 15
    list_display = ('id', 'relation_exp_app', 'is_active', 'check', 'score', 'comment', 'date_last')
    list_display_links = ('relation_exp_app',)
    list_filter = ('check',)
    fieldsets = (
        (None, {'fields': ('score', 'comment',)}),
        # ('Эксперты', {'fields': ('experts', )})
    )
    search_fields = ['relation_exp_app', 'check', ]
    ordering = ('relation_exp_app',)
    change_form_template = 'admin/score_one_admin.html'

    def load_from_relation(self, request):
        """
        Проверяем есть ли связи в общей комиссии, которые мы ещё не добавили, если есть, добавляем
        """
        self.model.objects.all().update()
        all_rel_exp_app = RelationExpertApplication.objects.all()
        now_score_objects = self.model.objects.all().values('relation_exp_app')
        id_rel_exp_app_now = []
        count = 0
        # Просто собираем все сущестующие свзяи в табличу
        for score_obj in now_score_objects:
            id_rel_exp_app_now.append(score_obj['relation_exp_app'])
        # проверяем есть ли связь уже
        for rel_exp_app in all_rel_exp_app:
            if rel_exp_app.id in id_rel_exp_app_now:
                print('YES', rel_exp_app)
            else:
                print('NO', rel_exp_app)
                if rel_exp_app.common_commission:  # обязательная проверка на общую комиссию
                    self.model.objects.create(relation_exp_app=rel_exp_app)
                    count += 1
        if count:
            self.message_user(request, "Объекты добавлены в количестве {} шт".format(count))
        else:
            self.message_user(request, "Нет объектов для добавления".format(count))
        return HttpResponseRedirect("../")


@admin.register(ScoreExpert)
class ScoreExpertCommissionAdmin(MyScoreBaseAdmin):
    list_per_page = 15
    list_display = ('id', 'relation_exp_app','is_active', 'check', 'score',
                    'score1', 'score2', 'score3', 'score4', 'score5', 'comment', 'date_last')
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
        self.model.objects.all().update()
        all_rel_exp_app = RelationExpertApplication.objects.all()
        now_score_objects = self.model.objects.all().values('relation_exp_app')
        id_rel_exp_app_now = []
        count = 0
        # Просто собираем все сущестующие свзяи в табличу
        for score_obj in now_score_objects:
            id_rel_exp_app_now.append(score_obj['relation_exp_app'])
        # проверяем есть ли связь уже
        for rel_exp_app in all_rel_exp_app:
            if rel_exp_app.id in id_rel_exp_app_now:
                print('YES', rel_exp_app)
            else:
                print('NO', rel_exp_app)
                if not rel_exp_app.common_commission:  # обязательная проверка на экспертную комиссию
                    self.model.objects.create(relation_exp_app=rel_exp_app)
                    count += 1
        if count:
            self.message_user(request, "Объекты добавлены в количестве {} шт".format(count))
        else:
            self.message_user(request, "Нет объектов для добавления".format(count))
        return HttpResponseRedirect("../")


@admin.register(ScoreCommonAll)
class ScoreAllCommonCommissionAdmin(MyScoreBaseAdmin):
    list_per_page = 15
    list_display = ('id', 'application', 'check', 'score', 'comment_master', 'date_last')
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
        self.model.objects.all().update()
        all_application = Application.objects.all()
        now_score_objects = self.model.objects.all().values('application')
        id_apps = []
        count = 0
        # Просто собираем все сущестующие свзяи в табличу
        for app in now_score_objects:
            id_apps.append(app['application'])

        # проверяем есть ли связь уже
        for app in all_application:
            if app.id in id_apps:
                pass
            else:
                self.model.objects.create(application=app)
                count += 1
        if count:
            self.message_user(request, "Объекты добавлены в количестве {} шт".format(count))
        else:
            self.message_user(request, "Нет объектов для добавления".format(count))
        return HttpResponseRedirect("../")


@admin.register(ScoreExpertAll)
class ScoreAllExpertCommissionAdmin(MyScoreBaseAdmin):
    list_per_page = 15
    list_display = ('id', 'application', 'check', 'score',
                    'score1', 'score2', 'score3', 'score4', 'score5', 'comment_master', 'date_last')
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
        self.model.objects.all().update()
        all_application = Application.objects.all()
        now_score_objects = self.model.objects.all().values('application')
        id_apps = []
        count = 0
        print(all_application)
        # Просто собираем все сущестующие свзяи в табличу
        for app in now_score_objects:
            id_apps.append(app['application'])
        print(id_apps)

        # проверяем есть ли связь уже
        for app in all_application:
            if app.id in id_apps:
                print('YES', app)
            else:
                print('NO', app)
                self.model.objects.create(application=app)
                count += 1
        if count:
            self.message_user(request, "Объекты добавлены в количестве {} шт".format(count))
        else:
            self.message_user(request, "Нет объектов для добавления".format(count))
        return HttpResponseRedirect("../")


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
        self.model.objects.all().update()
        all_application = Application.objects.all()
        now_score_objects = self.model.objects.all().values('application')
        id_apps = []
        count = 0
        print(all_application)
        # Просто собираем все сущестующие свзяи в табличу
        for app in now_score_objects:
            id_apps.append(app['application'])
        print(id_apps)

        # проверяем есть ли связь уже
        for app in all_application:
            if app.id in id_apps:
                print('YES', app)
            else:
                print('NO', app)
                self.model.objects.create(application=app)
                count += 1
        if count:
            self.message_user(request, "Объекты добавлены в количестве {} шт".format(count))
        else:
            self.message_user(request, "Нет объектов для добавления".format(count))
        return HttpResponseRedirect("../")



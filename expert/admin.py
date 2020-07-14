from django.contrib.admin import AdminSite
from info.models import FederalDistrict
from django.urls import path
from django.http import HttpResponseRedirect, HttpRequest
from django.contrib import messages
from score.models import ScoreCommon, ScoreExpert, ScoreAll, ScoreCommonAll, ScoreExpertAll
from score.function_upload import upload_all_score
from result.function_upload import upload_all_result
from result.models import CheckExpertScore, CheckGroups, CheckApplication
from expert.fuction_for_all import reload_scores

from .func_export import export_personal_info_request


class MyAdminSite(AdminSite):
    site_header = 'Админка Я - Эксперт'
    site_title = 'Я - Эксперт'
    index_title = 'Админка'
    index_template = 'admin/my_admin_index.html'

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            # path('update_score/', self.update_score),
            path('upload_score/', self.upload_score),
            path('export_score/', self.export_score),
            # path('update_result/', self.update_result),
            path('upload_result/', self.upload_result),
            path('export_result/', self.export_result),
            path('export_users/', self.export_users),
            path('load_users/', self.load_users),
            path('export_relation/', self.export_relation),
            path('load_relation/', self.load_relation),
        ]
        return my_urls + urls

    def export_users(self, request):

        # Выгружает личную инфу экспертов
        #log = 'Якобы выгрузил личную инфу экспертов'
        #messages.success(request, log)
        return export_personal_info_request(request)

    def load_users(self, request):
        # Загружает экспертов
        log = 'Якобы загрузили экспертов'
        messages.success(request, log)
        return HttpResponseRedirect("../")

    def export_relation(self, request):
        # Выгружает распределение экспертов
        log = 'Якобы выгрузил распределение экспертов'
        messages.success(request, log)
        return HttpResponseRedirect("../")

    def load_relation(self, request):
        # Загружает распределение экспертов
        log = 'Якобы загрузили распределение экспертов'
        messages.success(request, log)
        return HttpResponseRedirect("../")

    def update_score(self):
        # Подгружает новые объекты в score
        log = upload_all_score()
        # messages.success(request, log)
        return log


    def upload_score(self, request):
        log = self.update_score()
        # Обновляет оценки
        for mod in [ScoreCommon, ScoreExpert, ScoreCommonAll, ScoreExpertAll, ScoreAll]:
            reload_scores(mod)

        messages.success(request, 'Обновили оценки ' + log)
        return HttpResponseRedirect("../")

    def export_score(self, request):
        messages.success(request, 'Допустим выгрузили оценки') # TODO
        return HttpResponseRedirect("../")

    def update_result(self):
        log = upload_all_result()
        return log


    def upload_result(self, request):
        log = self.update_result()
        # Обновляем оценки
        for mod in [CheckExpertScore, CheckGroups, CheckApplication]:
            reload_scores(mod)
        messages.success(request, 'Обновили результаты ' + log)
        return HttpResponseRedirect("../")


    def export_result(self, request):
        messages.success(request, 'Допустим выгрузили  результаты') # TODO
        return HttpResponseRedirect("../")


    """
    def get_app_list(self, request):
        ordering = {
            "Эксперты": 1,
            "Комиссии": 2,
            "Федеральные округа": 3,
            "Регионы": 2,
            "Вузы/Организации": 1,
            "Направления": 3,
            "Заявки": 2,
            "Связи экспертов и заявок": 1,
            "Оценки экспертов ОК по заявке": 4,
            "Оценки экспертов ЭК по заявке": 4,
            "Все оценки ОК по заявке": 4,
            "Все оценки ЭК по заявке": 4,
            "Все оценки": 4,
            "Готовность оценок по эксперту": 4,
            'Готовность по группам': 4,
            'Готовность по заявкам': 4,
                    }
        app_dict = self._build_app_dict(request)
        app_list = sorted(app_dict.values(), key=lambda x: x['name'].lower())

        for app in app_list:
            app['models'].sort(key=lambda x: ordering[x['name']])
        return app_list
    """

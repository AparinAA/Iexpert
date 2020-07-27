from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import CreateView, UpdateView

from app.models import RelationExpertApplication, Application, Direction
from result.models import CheckExpertScore
from userexpert.models import CustomGroup, Expert

from score.models import ScoreExpert, ScoreCommon, ScoreCommonAll, ScoreExpertAll


def ExpertViews(request):
    # Админская страница просмотра эксперта
    if request.user.is_authenticated:
        current_user = Expert.objects.get(id=request.user.pk)
    else:
        raise PermissionDenied('Нет прав')
    if not current_user.is_admin:
        raise PermissionDenied('Нет прав')
    else:
        all_group = CustomGroup.objects.all().filter(admin_group=False)
        all_expert = Expert.objects.all()
        return render(request, 'userexpert/experts_list.html',
                      context={'all_group': all_group, 'all_expert': all_expert})


def ExpertOneViews(request, pk):
    # Админская страница просмотра эксперта
    if request.user.is_authenticated:
        current_user = Expert.objects.get(id=request.user.pk)
    else:
        raise PermissionDenied('Нет прав')
    if not current_user.is_admin and not current_user.master_group:
        raise PermissionDenied('Нет прав')
    elif not Expert.objects.all().get(id=pk).master_group:
        expert = Expert.objects.all().get(id=pk)
        all_application_set = RelationExpertApplication.objects.all().filter(expert=expert)
        application_all = []
        for app_expert in all_application_set:
            app = app_expert.get_application()
            application_all.append(app)
        if expert.common_commission:
            scores_common = ScoreCommon.objects.all().filter(relation_exp_app__in=all_application_set).filter(
                check=False)
            scores_expert = []
            check_common = ScoreCommon.objects.all().filter(relation_exp_app__in=all_application_set).filter(
                check=True)
            check_expert = []
        else:
            scores_expert = ScoreExpert.objects.all().filter(relation_exp_app__in=all_application_set).filter(
                check=False)
            scores_common = []
            check_expert = ScoreExpert.objects.all().filter(relation_exp_app__in=all_application_set).filter(
                check=True)
            check_common = []

        dict_score = {}
        dict_check = {}
        # Словарь
        commissions = expert.get_custom_commission

        for com in commissions:
            if not com.common_commission:
                all_dir = Direction.objects.filter(commission=com)
                all_app = Application.objects.filter(name__in=all_dir)
                all_rel = RelationExpertApplication.objects.all().filter(application__in=all_app).filter(expert=expert)
            else:
                all_dir = Direction.objects.all()
                all_app = Application.objects.filter(name__in=all_dir)
                all_rel = RelationExpertApplication.objects.all().filter(expert=expert).filter(application__in=all_app)
            if com.common_commission:
                sc = ScoreCommon.objects.all().filter(relation_exp_app__in=all_rel)
            else:
                sc = ScoreExpert.objects.all().filter(relation_exp_app__in=all_rel)
            score = sc.filter(check=False)
            check = sc.filter(check=True)
            dict_score[com] = score
            dict_check[com] = check

        # Подтверждение оценок
        try:
            check_score = CheckExpertScore.objects.all().get(expert=expert)
        except:
            check_score = []

        if current_user.is_admin:
            tempales = 'userexpert/expert_detail.html'
        else:
            com = current_user.get_commission_master
            try:
                dict_check = {com: dict_check[com]}
            except:
                dict_check = None
            try:
                dict_score = {com: dict_score[com]}
            except:
                dict_score = None

            tempales = 'userexpert/expert_master_detail.html'
        return render(request, tempales,
                      context={'expert': expert, 'application_all': application_all,
                               'scores_common': scores_common,
                               'scores_expert': scores_expert,
                               'check_common': check_common,
                               'check_expert': check_expert,
                               'check_score': check_score,
                               'dict_check': dict_check,
                               'dict_score': dict_score,
                               })
    else:
        expert = Expert.objects.all().get(id=pk)
        group = expert.get_commissions()
        cus_gr = CustomGroup.objects.all().get(group__in=group)  # ЗДЕСЬ ИМЕЕМ В ВИДУ, ЧТО ТОЛЬКО ОДНА КОМИССИЯ
        if cus_gr.common_commission:
            all_application = Application.objects.all()
            scores_common = ScoreCommonAll.objects.all().filter(application__in=all_application).filter(
                check=False)
            scores_expert = []
            check_common = ScoreCommonAll.objects.all().filter(application__in=all_application).filter(
                check=True)
            check_expert = []
        else:
            all_application = Application.objects.all().filter(name__commission__group__in=group)
            scores_expert = ScoreExpertAll.objects.all().filter(application__in=all_application).filter(
                check=False)
            scores_common = []
            check_expert = ScoreExpertAll.objects.all().filter(application__in=all_application).filter(
                check=True)
            check_common = []
        return render(request, 'userexpert/master_detail.html', context={
            'expert': expert,
            'scores_common': scores_common,
            'scores_expert': scores_expert,
            'check_common': check_common,
            'check_expert': check_expert,
        })


from result.models import CheckExpertScore
from expert.func_export import export_request, save_personal_info_to_woorksheet, export_personal_info
from expert.func_export import export_detailed_all_scores, save_detailed_scores_to_woorksheet
from expert.func_export import save_relation_s_to_woorksheet, export_relation

dict_commission = {'0': 'Аll',
                   "1": "Агропромышленный комплекс",
                   "2": "Вооружение и военная техника",
                   "3": "Естественные науки",
                   "4": "Инженерные науки и технологии",
                   "5": "Искусство и гуманитарные науки",
                   "6": "Компьютерные науки",
                   "7": "Медицина и здравоохранение",
                   "8": "Педагогические науки",
                   "9": "Социально-экономические науки",
                   "10": "Общая комиссия"}
from django.contrib.auth.models import Group


def ExperGroupOneViews(request, pk):
    try:
        if request.user.is_authenticated:
            current_user = Expert.objects.get(id=request.user.pk)
            commission = CustomGroup.objects.all().get(id=pk)
        else:
            raise PermissionDenied('Нет прав')
        if current_user.is_admin or current_user.get_commission_master == commission:
            if current_user.get_commission_master == commission:
                if 'pers_data' in request.POST:
                    name_commission = dict_commission[str(pk)]
                    commission = CustomGroup.objects.get(group=Group.objects.get(name=name_commission))
                    return export_request(request, commission, func_for_get_data_all=export_personal_info,
                                          func_for_woorksheet=save_personal_info_to_woorksheet,
                                          namefile='Перс. данные', dop_name="Личная информация")
                elif 'all_result' in request.POST:

                    name_commission = dict_commission[str(pk)]
                    commission = CustomGroup.objects.get(group=Group.objects.get(name=name_commission))
                    return export_request(request, commission, func_for_get_data_all=export_detailed_all_scores,
                                          func_for_woorksheet=save_detailed_scores_to_woorksheet,
                                          namefile='Подробный рейтинг.', dop_name="Подробный рейтинг")
                elif 'realtion' in request.POST:
                    name_commission = dict_commission[str(pk)]
                    commission = CustomGroup.objects.get(group=Group.objects.get(name=name_commission))
                    return export_request(request, commission, func_for_get_data_all=export_relation,
                                          func_for_woorksheet=save_relation_s_to_woorksheet,
                                          namefile='Распределение', dop_name="Распределение экспертов")
                else:
                    all_expert = Expert.objects.all().filter(groups=commission.group)
                    check_exp_sc = CheckExpertScore.objects.all().filter(expert__in=all_expert)
                    return render(request, 'userexpert/commission_master_detail.html',
                                  context={
                                      'commission': commission,
                                      'all_experts': all_expert,
                                      'check_experts': check_exp_sc
                                  })
            else:
                all_direction = Direction.objects.all().filter(commission=commission)
                all_application = Application.objects.all().filter(name__in=all_direction)
                all_expert = Expert.objects.all().filter(groups=commission.group)
                return render(request, 'userexpert/commission_detail.html',
                              context={
                                  'all_application': all_application,
                                  'commission': commission,
                                  'all_experts': all_expert
                              })
        else:
            raise PermissionDenied('Нет прав')

    except:
        raise PermissionDenied('Нет прав')


from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView


class ExpertUpdate(PermissionRequiredMixin, UpdateView):
    model = Expert
    fields = ['email', 'phone', 'position']
    permission_required = 'userexpert.chage_expert'
    template_name = 'userexpert/expert_update.html'

    def has_permission(self, *args, **kwargs):
        perms = self.get_permission_required()
        pk_ = self.kwargs['pk']
        if self.request.user.is_staff:
            return True
        if self.request.user.has_perms(perms):
            return True
        if self.model.objects.all().get(pk=pk_) == self.request.user:
            return True
        else:
            return False

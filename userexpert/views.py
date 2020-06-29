from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import CreateView, UpdateView

from app.models import RelationExpertApplication, Application, Direction
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
        if current_user.is_admin:
            tempales = 'userexpert/expert_detail.html'
        else:
            tempales = 'userexpert/expert_master_detail.html'
        return render(request, tempales,
                      context={'expert': expert, 'application_all': application_all,
                               'scores_common': scores_common,
                               'scores_expert': scores_expert,
                               'check_common': check_common,
                               'check_expert': check_expert
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


def ExperGroupOneViews(request, pk):
    try:
        if request.user.is_authenticated:
            current_user = Expert.objects.get(id=request.user.pk)
            commission = CustomGroup.objects.all().get(id=pk)
        else:
            raise PermissionDenied('Нет прав')
        if current_user.is_admin or current_user.get_commission_master == commission:
            if current_user.get_commission_master == commission:
                all_direction = Direction.objects.all().filter(commission=commission)
                all_application = Application.objects.all().filter(name__in=all_direction)
                all_expert = Expert.objects.all().filter(groups=commission.group)
                return render(request, 'userexpert/commission_master_detail.html',
                              context={
                                  'all_application': all_application,
                                  'commission': commission,
                                  'all_experts': all_expert
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


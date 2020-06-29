from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.views.generic import CreateView, UpdateView

from app.models import Application, RelationExpertApplication
from info.models import Company, FederalDistrict, Region
from django.views import generic

from userexpert.models import CustomGroup


def ApplicationView(request):
    if request.user.is_admin:
        all_group = CustomGroup.objects.all()
        all_application = Application.objects.all()
        return render(request, 'app/app_list.html',
                      context={'all_group': all_group, 'all_application': all_application})
    else:
        raise PermissionDenied('Нет прав')


def ApplicationOneView(request, pk):
    if request.user.is_admin:
        application = Application.objects.all().filter(id=pk)[0]
        all_expert_set = RelationExpertApplication.objects.all().filter(application=application)
        all_expert_com_com = []
        all_expert_exp_com = []

        for expert_app in all_expert_set:
            expert = expert_app.get_expert()
            if expert.common_commission:
                all_expert_com_com.append(expert)
            else:
                all_expert_exp_com.append(expert)
        return render(request, 'app/app_detail.html',
                      context={'application': application,
                               'all_expert_com_com': all_expert_com_com,
                               'all_expert_exp_com': all_expert_exp_com
                               })
    else:
        raise PermissionDenied('Нет прав')


class ApplicationCreate(PermissionRequiredMixin, CreateView):
    model = Application
    template_name = 'app/app_form.html'
    fields = '__all__'
    permission_required = 'app.create_application'

    def has_permission(self, *args, **kwargs):
        perms = self.get_permission_required()
        if self.request.user.is_staff:
            return True
        if self.request.user.has_perms(perms):
            return True
        else:
            return False


class ApplicationUpdate(PermissionRequiredMixin, UpdateView):
    model = Application
    template_name = 'app/app_update.html'
    fields = ['link_archiv']
    permission_required = 'app.change_application'

    def has_permission(self, *args, **kwargs):
        perms = self.get_permission_required()
        if self.request.user.is_staff:
            return True
        if self.request.user.has_perms(perms):
            return True
        else:
            return False
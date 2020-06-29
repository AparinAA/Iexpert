from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.http import HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.contrib.auth.decorators import user_passes_test, login_required, permission_required
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from score.models import ScoreExpert, ScoreCommon, ScoreExpertAll, ScoreCommonAll
from userexpert.models import CustomGroup


class ScoreCommonOne(PermissionRequiredMixin, UpdateView):
    # Форма оценки
    model = ScoreCommon
    template_name = 'score/score_common_form.html'
    fields = ['score', 'comment']
    permission_required = ['score.change_scorecommon']

    def has_permission(self, *args, **kwargs):
        perms = self.get_permission_required()
        pk_ = self.kwargs['pk']
        if self.request.user.is_staff:
            return True
        if self.model.objects.all().get(pk=pk_).relation_exp_app.expert == self.request.user:
            return self.request.user.has_perms(perms)
        else:
            return False


def ScoreCommonOneView(request, pk):
    if request.user.has_perm('score.view_scorecommon') or request.user.is_staff:
        SCC = ScoreCommon.objects.all().filter(id=pk)[0]
        if SCC.relation_exp_app.expert == request.user or request.user.is_staff:
            return render(request, 'score/score_common_detail.html',
                          context={'scorecommon': SCC})
    raise PermissionDenied('Нет прав')


class ScoreExpertOne(PermissionRequiredMixin, UpdateView):
    # Форма оценки
    model = ScoreExpert
    template_name = 'score/score_expert_form.html'
    fields = ['score1', 'score2', 'score3', 'score4', 'score5', 'comment']
    permission_required = ['score.change_scoreexpert']

    def has_permission(self, *args, **kwargs):
        perms = self.get_permission_required()
        pk_ = self.kwargs['pk']
        if self.request.user.is_staff:
            return True
        if self.model.objects.all().get(pk=pk_).relation_exp_app.expert == self.request.user:
            return self.request.user.has_perms(perms)
        else:
            return False


def ScoreExpertOneView(request, pk):
    if request.user.has_perm('score.view_scoreexpert') or request.user.is_staff:
        SEC = ScoreExpert.objects.all().filter(id=pk)[0]
        if SEC.relation_exp_app.expert == request.user or request.user.is_staff:
            return render(request, 'score/score_expert_detail.html',
                          context={'scoreexpert': SEC})
    raise PermissionDenied('Нет прав')


def ScoreCommonAllView(request, pk):
    if request.user.has_perm('score.view_scorecommonall') or request.user.is_staff:
        sco_all = ScoreCommonAll.objects.all().filter(id=pk)[0]
        return render(request, 'score/score_common_all_detail.html',
                      context={'score_all': sco_all})
    else:
        raise PermissionDenied('Нет прав')


class ScoreCommonAllForm(PermissionRequiredMixin, UpdateView):
    # Форма оценки
    model = ScoreCommonAll
    template_name = 'score/score_common_all_form.html'
    fields = ['comment_master']
    permission_required = ['score.change_scorecommonall']

    def has_permission(self, *args, **kwargs):
        perms = self.get_permission_required()
        pk_ = self.kwargs['pk']
        if self.request.user.is_staff:
            return True
        master_gr = CustomGroup.objects.all().get(master=self.request.user)
        if master_gr.common_commission:
            return self.request.user.has_perms(perms)
        else:
            return False


def ScoreExpertAllView(request, pk):
    if request.user.has_perm('score.view_scoreexpertall'):
        sco_all = ScoreExpertAll.objects.all().filter(id=pk)[0]
        if sco_all.application.name.commission.master == request.user or request.user.is_staff:
            return render(request, 'score/score_expert_all_detail.html',
                          context={'score_all': sco_all})
    else:
        raise PermissionDenied('Нет прав')


class ScoreExpertAllForm(PermissionRequiredMixin, UpdateView):
    # Форма оценки
    model = ScoreExpertAll
    template_name = 'score/score_expert_all_form.html'
    fields = ['comment_master']
    permission_required = ['score.change_scoreexpertall']

    def has_permission(self, *args, **kwargs):
        perms = self.get_permission_required()
        pk_ = self.kwargs['pk']
        if self.request.user.is_staff:
            return True
        if self.model.objects.all().get(pk=pk_).application.name.commission.master == self.request.user:
            return self.request.user.has_perms(perms)
        else:
            return False

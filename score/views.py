from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.forms import Textarea,Select
from django.http import HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.contrib.auth.decorators import user_passes_test, login_required, permission_required
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from score.models import ScoreExpert, ScoreCommon, ScoreExpertAll, ScoreCommonAll
from userexpert.models import CustomGroup
from django.forms.models import modelform_factory


class ScoreCommonOne(PermissionRequiredMixin, UpdateView):
    # Форма оценки
    model = ScoreCommon
    template_name = 'score/score_common_form.html'
    # fields = ['score', 'comment']
    form_class = modelform_factory(ScoreCommon, fields=['score', 'comment'],
                                   widgets={
                                   "comment": Textarea(attrs={'rows': 6, 'cols': 80, 'class' : 'col-md-12 form-control'}),
                                    "score" : Select(attrs={'class' : 'col-md-12 form-control'}),
                                   })
    permission_required = ['score.change_scorecommon']

    def has_permission(self, *args, **kwargs):
        perms = self.get_permission_required()
        pk_ = self.kwargs['pk']
        if self.request.user.is_staff:
            return True
        if self.model.objects.all().get(pk=pk_).relation_exp_app.expert == self.request.user:
            check = CheckExpertScore.objects.get(expert=self.request.user).check_exp
            if not check:
                return self.request.user.has_perms(perms)
            else:
                return False
        else:
            return False


def ScoreCommonOneView(request, pk):
    if request.user.has_perm('score.view_scorecommon') or request.user.is_staff:
        SCC = ScoreCommon.objects.all().filter(id=pk)[0]
        if SCC.relation_exp_app.expert == request.user or request.user.is_staff:
            check = CheckExpertScore.objects.get(expert=SCC.relation_exp_app.expert)
            return render(request, 'score/score_common_detail.html',
                          context={'scorecommon': SCC,
                                   'check_exp': check})
    raise PermissionDenied('Нет прав')


class ModelFormWidgetMixin(PermissionRequiredMixin):
    def get_form_class(self):
        return modelform_factory(self.model, fields=self.fields, widgets=self.widgets)


class ScoreExpertOne(PermissionRequiredMixin, UpdateView):
    # Форма оценки
    model = ScoreExpert

    template_name = 'score/score_expert_form.html'

    form_class = modelform_factory(ScoreExpert, fields=['score1', 'score2', 'score3', 'score4', 'score5', 'comment'],
                                   widgets={
                                   "comment": Textarea(attrs={'rows': 6, 'cols': 80, 'class' : 'col-md-12 form-control'}),
                                   "score1" : Select(attrs={'class' : 'col-md-12 form-control'}),
                                   "score2" : Select(attrs={'class' : 'col-md-12 form-control'}),
                                   "score3" : Select(attrs={'class' : 'col-md-12 form-control'}),
                                   "score4" : Select(attrs={'class' : 'col-md-12 form-control'}),
                                   "score5" : Select(attrs={'class' : 'col-md-12 form-control'}),
                                   })

    # widgets = {"comment": Textarea(attrs={'rows': 2, 'cols': 80})}

    permission_required = ['score.change_scoreexpert']

    def has_permission(self, *args, **kwargs):
        perms = self.get_permission_required()
        pk_ = self.kwargs['pk']
        if self.request.user.is_staff:
            return True
        if self.model.objects.all().get(pk=pk_).relation_exp_app.expert == self.request.user:
            check = CheckExpertScore.objects.get(expert=self.request.user).check_exp
            if not check:
                return self.request.user.has_perms(perms)
            else:
                return False
        else:
            return False


from result.models import CheckExpertScore, ResultMaster


def ScoreExpertOneView(request, pk):
    if request.user.has_perm('score.view_scoreexpert') or request.user.is_staff:
        SEC = ScoreExpert.objects.all().filter(id=pk)[0]
        if SEC.relation_exp_app.expert == request.user or request.user.is_staff:
            check = CheckExpertScore.objects.get(expert=SEC.relation_exp_app.expert)
            return render(request, 'score/score_expert_detail.html',
                          context={'scoreexpert': SEC,
                                   'check_exp': check})

    raise PermissionDenied('Нет прав')


def ScoreCommonAllView(request, pk):
    if request.user.has_perm('score.view_scorecommonall') or request.user.is_staff:
        sco_all = ScoreCommonAll.objects.all().filter(id=pk)[0]
        if request.user.master_group:
            result_master = ResultMaster.objects.get(master=request.user)
        else:
            result_master = {}
            result_master['status'] = 'w'
        return render(request, 'score/score_common_all_detail.html',
                      context={'score_all': sco_all,
                               'result_master': result_master})
    else:
        raise PermissionDenied('Нет прав')


class ScoreCommonAllForm(PermissionRequiredMixin, UpdateView):
    # Форма оценки
    model = ScoreCommonAll
    template_name = 'score/score_common_all_form.html'
    # fields = ['comment_master']
    form_class = modelform_factory(ScoreCommonAll, fields=['comment_master'],
                                   widgets={"comment_master": Textarea(attrs={'rows': 6, 'cols': 80, 'class' : 'col-md-12 form-control'})})
    permission_required = ['score.change_scorecommonall']

    def has_permission(self, *args, **kwargs):
        perms = self.get_permission_required()
        pk_ = self.kwargs['pk']
        if self.request.user.is_staff:
            return True
        master_gr = CustomGroup.objects.all().get(master=self.request.user)
        if master_gr.common_commission:
            if ResultMaster.objects.get(master=self.request.user).status != 'w':
                return False
            if self.model.objects.all().get(pk=pk_).check:
                return False
            else:
                return self.request.user.has_perms(perms)
        else:
            return False


def ScoreExpertAllView(request, pk):
    if request.user.has_perm('score.view_scoreexpertall'):
        sco_all = ScoreExpertAll.objects.all().filter(id=pk)[0]
        if request.user.master_group:
            result_master = ResultMaster.objects.get(master=request.user)
        else:
            result_master = {}
            result_master['status'] = 'w'
        if sco_all.application.name.commission.master == request.user or request.user.is_staff:
            return render(request, 'score/score_expert_all_detail.html',
                          context={'score_all': sco_all,
                                   'result_master': result_master})
    else:
        raise PermissionDenied('Нет прав')


class ScoreExpertAllForm(PermissionRequiredMixin, UpdateView):
    # Форма оценки
    model = ScoreExpertAll
    template_name = 'score/score_expert_all_form.html'
    # fields = ['comment_master']
    form_class = modelform_factory(ScoreExpertAll, fields=['comment_master'],
                                   widgets={"comment_master": Textarea(attrs={'rows': 6, 'cols': 80, 'class' : 'col-md-12 form-control'})})
    permission_required = ['score.change_scoreexpertall']

    def has_permission(self, *args, **kwargs):
        perms = self.get_permission_required()
        pk_ = self.kwargs['pk']
        if self.request.user.is_staff:
            return True
        if self.model.objects.all().get(pk=pk_).application.name.commission.master == self.request.user:
            if ResultMaster.objects.get(master=self.request.user).status != 'w':
                return False
            if self.model.objects.all().get(pk=pk_).check:
                return False
            else:
                return self.request.user.has_perms(perms)
        else:
            return False

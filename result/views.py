from django.shortcuts import render
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.views.generic.edit import CreateView, UpdateView, DeleteView


# Create your views here.
from result.models import CheckExpertScore


class AllScoreForExpertForm(PermissionRequiredMixin, UpdateView):
    model = CheckExpertScore
    template_name = 'result/score_all_for_expert.html'
    fields = ['check_exp']
    permission_required = ['score.change_scoreexpert']

    def has_permission(self, *args, **kwargs):
        perms = self.get_permission_required()
        pk_ = self.kwargs['pk']
        if self.request.user.is_staff:
            return True
        print(self.model.objects.all().get(pk=pk_).expert)
        print(self.request.user)
        if self.model.objects.all().get(pk=pk_).expert == self.request.user:
            return self.request.user.has_perms(perms)
        else:
            return False

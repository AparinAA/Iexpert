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
    permission_required = ('score.change_scoreexpert', 'score.change_scorecommon')

    def has_permission(self, *args, **kwargs):
        perms = self.get_permission_required()
        pk_ = self.kwargs['pk']
        if self.request.user.is_staff:
            return True
        if self.model.objects.all().get(pk=pk_).expert == self.request.user:
            return self.request.user.has_perms_or(perms)
        else:
            return False

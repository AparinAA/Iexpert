from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django import forms


# Create your views here.

from result.models import CheckExpertScore


class UserForm(forms.ModelForm):
    YES_NO = ((True, 'Да'), (False, 'Нет'))
    check_exp = forms.BooleanField(
        #widget=forms.RadioSelect(choices=YES_NO)
    )

    class Meta:
        model = CheckExpertScore
        fields = ['check_exp']

    """def save(self, *args, **kwargs):
        print('save forms')
        super(UserForm, self).__save__(*args, **kwargs)
    """

class AllScoreForExpertForm(PermissionRequiredMixin, UpdateView):
    model = CheckExpertScore
    template_name = 'result/score_all_for_expert.html'
    #fields = ['check_exp']
    permission_required = ('score.change_scoreexpert', 'score.change_scorecommon')
    form_class = UserForm

    def has_permission(self, *args, **kwargs):
        perms = self.get_permission_required()
        pk_ = self.kwargs['pk']
        if self.request.user.is_staff:
            return True
        if self.model.objects.all().get(pk=pk_).expert == self.request.user:
            return self.request.user.has_perms_or(perms)
        else:
            return False



def AllScoreForExpertIndex(request):
    perms = ('score.change_scoreexpert', 'score.change_scorecommon')
    # if request.method == "POST":
    if request.user.is_staff:
        return render(request, 'check_admin.html')
    if request.user.has_perms_or(perms) or request.user.is_staff:
        if request.method == 'GET':
            try:
                check_exp_sc = CheckExpertScore.objects.all().get(expert=request.user)
                userform = UserForm()
                return render(request, 'result/score_all_for_expert.html',
                                context={'checkexpertscore': check_exp_sc,
                                         'form': userform})
            except:
                pass
        elif request.method == 'POST':
            form = UserForm(request.POST)
            if form.is_valid():
                # data = form.save(commit=False)
                check_exp_sc = CheckExpertScore.objects.all().get(expert=request.user)
                check_exp_sc.check_exp = form.cleaned_data['check_exp']

                return render(request, 'result/score_all_for_expert.html',
                              context={'checkexpertscore': check_exp_sc,
                                       'form': form})
    raise PermissionDenied('Нет прав')



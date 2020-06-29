from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from userexpert.models import CustomGroup, Expert
from app.models import Direction, Application
from info.models import Company, FederalDistrict, Region
from django.views import generic
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView

# Create your views here.
def CompanyView(request):
    if request.user.is_admin:
        all_company = Company.objects.all()
        all_fo = FederalDistrict.objects.all()
        return render(request, 'info/company_list.html',
                      context={'all_company': all_company, 'all_fo': all_fo})
    else:
        raise PermissionDenied('Нет прав')

def CompanyOneView(request, pk):
    if request.user.is_admin:
        company = Company.objects.all().filter(id=pk)[0]
        all_expert = Expert.objects.all().filter(company=company)
        all_application = Application.objects.all().filter(vuz=company)
        print(all_expert)
        return render(request, 'info/company_detail.html',
                      context={'company': company, 'all_expert': all_expert,
                               'all_application': all_application})
    else:
        raise PermissionDenied('Нет прав')

class CompanyCreate(PermissionRequiredMixin, CreateView):
    model = Company
    template_name = 'info/company_form.html'
    fields = '__all__'
    permission_required = 'info.create_company'

    def has_permission(self, *args, **kwargs):
        perms = self.get_permission_required()
        if self.request.user.is_staff:
            return True
        if self.request.user.has_perms(perms):
            return True
        else:
            return False

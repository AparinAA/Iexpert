from django.shortcuts import render

from score.models import ScoreCommon, ScoreExpert, ScoreCommonAll, ScoreExpertAll
from userexpert.models import CustomGroup, Expert
from app.models import  Direction, Application, RelationExpertApplication
from info.models import Company, FederalDistrict, Region
from django.views import generic


def index(request):
    num_application = Application.objects.all().count()
    num_direction = Direction.objects.all().count()
    num_expert = Expert.objects.all().filter(is_admin=False).count()
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    if request.user.is_authenticated:
        if request.user.is_master_group:
            expert = Expert.objects.all().filter(id=request.user.pk)[0]
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
            print(scores_expert)
            return render(request, 'index_master.html', context={
                'expert': expert,
                'scores_common': scores_common,
                'scores_expert': scores_expert,
                'check_common': check_common,
                'check_expert': check_expert,
            })
        else:
            expert = Expert.objects.all().filter(id=request.user.pk)[0]
            rel_exp_gr = expert.get_commissions()
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

            return render(request, 'index_expert.html', context={
                'expert': expert, 'application_all': application_all,
                'rel_exp_gr': rel_exp_gr,
                'scores_common': scores_common,
                'scores_expert': scores_expert,
                'check_common': check_common,
                'check_expert': check_expert,
            })
    else:
        return render(request, 'index.html',
                      context={'num_application': num_application, 'num_direction': num_direction,
                               'num_expert': num_expert,
                               'num_visits': num_visits})

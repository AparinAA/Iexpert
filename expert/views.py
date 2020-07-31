from django.shortcuts import render, redirect

from score.models import ScoreCommon, ScoreExpert, ScoreCommonAll, ScoreExpertAll
from userexpert.models import CustomGroup, Expert
from app.models import Direction, Application, RelationExpertApplication
from info.models import Company, FederalDistrict, Region
from django.views import generic
from result.models import CheckExpertScore, ResultMaster


def index(request):
    num_application = Application.objects.all().count()
    num_direction = Direction.objects.all().count()
    num_expert = Expert.objects.all().filter(is_admin=False).count()
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    if request.user.is_authenticated:  # Если человек авторизован
        if request.user.is_master_group:  # Отправляем на страницу ответственного секретаря
            expert = Expert.objects.all().filter(id=request.user.pk)[0]
            group = expert.get_commissions()
            cus_gr = CustomGroup.objects.all().get(
                group__in=group)  # ЗДЕСЬ ИМЕЕМ В ВИДУ, ЧТО ТОЛЬКО ОДНА КОМИССИЯ у секретаря
            res = ResultMaster.objects.get(master=expert)

            if cus_gr.common_commission:
                all_application = Application.objects.all()
                scores_common = ScoreCommonAll.objects.all().filter(application__in=all_application).filter(
                    check=False)
                check_common = ScoreCommonAll.objects.all().filter(application__in=all_application).filter(
                    check=True)

                # Строим словарь по оценке определять сколько экспертов начали и всего есть
                all_relation = RelationExpertApplication.objects.filter(common_commission=True).filter(
                    application__in=all_application)
                all_score = ScoreCommon.objects.filter(relation_exp_app__in=all_relation)
                # Словарь с заявками для оценки
                dict_score = {}
                for sc_app in scores_common:
                    rel_app = all_relation.filter(application=sc_app.application)
                    score_app = all_score.filter(relation_exp_app__in=rel_app)
                    dict_score[sc_app] = (score_app.filter(check=True).count(), score_app.count())

                dict_check = {}
                # Словарь со всеми заявками
                dict_all_score = {}
                for sc_app in ScoreCommonAll.objects.all().filter(application__in=all_application):
                    rel_app = all_relation.filter(application=sc_app.application)
                    score_app = all_score.filter(relation_exp_app__in=rel_app)
                    dict_all_score[sc_app] = (score_app.filter(check=True).count(), score_app.count())


                scores_expert = []
                check_expert = []
            else:
                all_application = Application.objects.all().filter(name__commission__group__in=group)
                scores_expert = ScoreExpertAll.objects.all().filter(application__in=all_application).filter(
                    check=False)
                check_expert = ScoreExpertAll.objects.all().filter(application__in=all_application).filter(
                    check=True)

                # Строим словарь по оценке определять сколько экспертов начали и всего есть
                all_relation = RelationExpertApplication.objects.filter(common_commission=False).filter(
                    application__in=all_application)
                all_score = ScoreExpert.objects.filter(relation_exp_app__in=all_relation)
                dict_score = {} # Словарь с заявками для оценки
                for sc_app in scores_expert:
                    rel_app = all_relation.filter(application=sc_app.application)
                    score_app = all_score.filter(relation_exp_app__in=rel_app)
                    dict_score[sc_app] = (score_app.filter(check=True).count(), score_app.count())
                # Словарь со всеми заявками
                dict_all_score = {}
                for sc_app in ScoreExpertAll.objects.all().filter(application__in=all_application):
                    rel_app = all_relation.filter(application=sc_app.application)
                    score_app = all_score.filter(relation_exp_app__in=rel_app)
                    dict_all_score[sc_app] = (score_app.filter(check=True).count(), score_app.count())

                # Строим словарь по оценке определять сколько экспертов всего есть
                dict_check = {}

                scores_common = []
                check_common = []

            return render(request, 'index_master.html', context={
                'expert': expert,
                'scores_common': scores_common,
                'scores_expert': scores_expert,
                'check_common': check_common,
                'check_expert': check_expert,
                'dict_score': dict_score,
                'dict_check': dict_check,
                'result_master': res,
                'dict_all_score': dict_all_score
            })
        else:  # Все остальные
            expert = Expert.objects.all().filter(id=request.user.pk)[0]
            commissions = expert.get_custom_commission
            all_application_set = RelationExpertApplication.objects.all().filter(expert=expert)
            application_all = []
            for app_expert in all_application_set:
                app = app_expert.get_application()
                application_all.append(app)

            # Эксперт общей комиссии и его оценки
            try:
                sc_common = ScoreCommon.objects.all().filter(relation_exp_app__in=all_application_set)
                scores_common = sc_common.filter(check=False)
                check_common = sc_common.filter(check=True)
            except:
                scores_common = []
                check_common = []

            # Эксперт экспертной комиссии и его оценки
            try:
                sc_exp = ScoreExpert.objects.all().filter(relation_exp_app__in=all_application_set)
                scores_expert = sc_exp.filter(check=False)
                check_expert = sc_exp.filter(check=True)
            except:
                scores_expert = []
                check_expert = []

            dict_score = {}
            dict_check = {}
            # Словарь
            for com in commissions:
                if not com.common_commission:
                    all_dir = Direction.objects.filter(commission=com)
                    all_app = Application.objects.filter(name__in=all_dir)
                    all_rel = RelationExpertApplication.objects.all().filter(application__in=all_app).filter(
                        expert=expert)
                else:
                    all_dir = Direction.objects.all()
                    all_app = Application.objects.filter(name__in=all_dir)
                    all_rel = RelationExpertApplication.objects.all().filter(expert=expert).filter(
                        application__in=all_app)
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

            return render(request, 'index_expert.html', context={
                'expert': expert, 'application_all': application_all,
                'commissions': commissions,
                'scores_common': scores_common,
                'scores_expert': scores_expert,
                'check_common': check_common,
                'check_expert': check_expert,
                'check_score': check_score,
                'dict_check': dict_check,
                'dict_score': dict_score,
            })
    else:
        return render(request, 'index.html',
                      context={'num_application': num_application, 'num_direction': num_direction,
                               'num_expert': num_expert,
                               'num_visits': num_visits})


def criteria_expert(request):
    return render(request, 'criteria_expert.html', )


def criteria_common(request):
    return render(request, 'criteria_common.html', )

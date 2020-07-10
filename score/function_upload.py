from score.models import ScoreCommon, ScoreExpert, ScoreAll, ScoreCommonAll, ScoreExpertAll
from app.models import Application, RelationExpertApplication
from import_export.admin import ImportExportActionModelAdmin


def upload_all_score():
    count_com = upload_score_common()
    count_exp = upload_score_expert()
    count_com_all = upload_score_all(ScoreCommonAll)
    count_exp_all = upload_score_all(ScoreExpertAll)
    count_all = upload_score_all(ScoreAll)
    log = "Оценок экспертов ОК по заявкам: {}\nОценок экспертов ЭК по заявкам: {}\nОценок экспертов ОК: {}\nОценок экспертов ЭК: {}\nОценок всего: {}".format(
        count_com, count_exp, count_com_all, count_exp_all, count_all)
    return log

def upload_score_common():
    model = ScoreCommon
    model.objects.all().update()
    all_rel_exp_app = RelationExpertApplication.objects.all()
    now_score_objects = model.objects.all().values('relation_exp_app')
    id_rel_exp_app_now = []
    count = 0
    for score_obj in now_score_objects:
        id_rel_exp_app_now.append(score_obj['relation_exp_app'])
    # проверяем есть ли связь уже
    for rel_exp_app in all_rel_exp_app:
        if rel_exp_app.id in id_rel_exp_app_now:
            pass
        else:
            if rel_exp_app.common_commission:  # обязательная проверка на общую комиссию
                model.objects.create(relation_exp_app=rel_exp_app)
                count += 1
    return count


def upload_score_expert():
    model = ScoreExpert
    model.objects.all().update()
    all_rel_exp_app = RelationExpertApplication.objects.all()
    now_score_objects = model.objects.all().values('relation_exp_app')
    id_rel_exp_app_now = []
    count = 0
    # Просто собираем все сущестующие свзяи в табличу
    for score_obj in now_score_objects:
        id_rel_exp_app_now.append(score_obj['relation_exp_app'])
    # проверяем есть ли связь уже
    for rel_exp_app in all_rel_exp_app:
        if rel_exp_app.id in id_rel_exp_app_now:
            pass
        else:
            if not rel_exp_app.common_commission:  # обязательная проверка на экспертную комиссию
                model.objects.create(relation_exp_app=rel_exp_app)
                count += 1
    return count


def upload_score_all(model):
    model.objects.all().update()
    all_application = Application.objects.all()
    now_score_objects = model.objects.all().values('application')
    id_apps = []
    count = 0
    # Просто собираем все сущестующие свзяи в табличу
    for app in now_score_objects:
        id_apps.append(app['application'])

    # проверяем есть ли связь уже
    for app in all_application:
        if app.id in id_apps:
            pass
        else:
            model.objects.create(application=app)
            count += 1
    return count

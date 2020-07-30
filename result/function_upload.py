from app.models import Application
from result.models import CheckExpertScore
from userexpert.models import Expert, CustomGroup

def upload_all_result():
    count_exp = upload_expert()
    count_app = upload_app()
    count_gt = upload_group()
    log = "Выгрузили новые результаты: Эксперты: {}, Заявки: {}, Группы: {}".format(count_exp, count_app, count_gt)
    return log

def upload_expert():
    model = CheckExpertScore
    model.objects.all().update()
    all_expert = Expert.objects.all().filter(master_group=False).filter(is_admin=False)

    now_obj = model.objects.all().values('expert')
    id_exps = []
    count = 0
    # Просто собираем все сущестующие свзяи в табличу
    for exp in now_obj:
        id_exps.append(exp['expert'])

    for exp in all_expert:
        if exp.id in id_exps:
            pass
        else:
            model.objects.create(expert=exp)
            count += 1
    return count


def upload_group():
    model = CheckGroups
    model.objects.all().update()
    all_commission = CustomGroup.objects.all().filter(admin_group=False)

    now_obj = model.objects.all().values('commission')
    id_comm = []
    count = 0
    # Просто собираем все сущестующие свзяи в табличу
    for comm in now_obj:
        id_comm.append(comm['commission'])

    for comm in all_commission:
        if comm.id in id_comm:
            pass
        else:
            model.objects.create(commission=comm)
            count += 1
    return count


def upload_app():
    model = CheckApplication
    model.objects.all().update()
    all_app = Application.objects.all()

    now_obj = model.objects.all().values('application')
    id_apps = []
    count = 0
    # Просто собираем все сущестующие свзяи в табличу
    for app in now_obj:
        id_apps.append(app['application'])

    for app in all_app:
        if app.id in id_apps:
            pass
        else:
            model.objects.create(application=app)
            count += 1
    return count

from app.models import Application
from result.models import CheckExpertScore, ResultMaster
from userexpert.models import Expert, CustomGroup

def upload_all_result():
    count_exp = upload_expert()
    #count_app = upload_app()
    #count_gt = upload_group()
    count_master = upload_master()
    log = "Выгрузили новые результаты: Эксперты: {}, Ответственные секретари: {}, ".format(count_exp, count_master)
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

def upload_master():
    model = ResultMaster
    model.objects.all().update()
    all_expert = Expert.objects.all().filter(master_group=True).filter(is_admin=False)

    now_obj = model.objects.all().values('master')
    id_exps = []
    count = 0
    # Просто собираем все сущестующие свзяи в табличу
    for exp in now_obj:
        id_exps.append(exp['master'])

    for exp in all_expert:
        if exp.id in id_exps:
            pass
        else:
            model.objects.create(master=exp)
            count += 1
    return count


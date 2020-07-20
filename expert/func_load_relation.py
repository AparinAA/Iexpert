import zipfile
from datetime import datetime
from sys import path
import io

import tablib
from django.http import HttpResponse, HttpResponseRedirect
import pandas as pd
from django.shortcuts import render
from django.contrib.auth.models import Group
from userexpert.models import Expert, CustomGroup
from app.models import Application, Direction, RelationExpertApplication
from info.models import Company
from django.contrib import messages

dict_commission = {'0': 'Аll',
                   "1": "Агропромышленный комплекс",
                   "2": "Вооружение и военная техника",
                   "3": "Естественные науки",
                   "4": "Инженерные науки и технологии",
                   "5": "Искусство и гуманитарные науки",
                   "6": "Компьютерные науки",
                   "7": "Медицина и здравоохранение",
                   "8": "Педагогические науки",
                   "9": "Социально-экономические науки",
                   "10": "Общая комиссия"}

from io import BytesIO
import openpyxl
from django.shortcuts import render
from django.conf import settings
from django.core.files.storage import FileSystemStorage


def func_load_relation(request):
    def find_app(app, commission):
        try:
            name, vuz = app.split(' - ')
            direct = Direction.objects.filter(name=name).get(commission=commission)
            vuz = Company.objects.get(short_name=vuz)
            application = Application.objects.filter(name=direct).filter(vuz=vuz)
            if application.count() != 1:
                return False, app
            else:
                return True, application.get()
        except:
            return False, app

    def find_expert(exp, commission):
        if exp != '-':
            try:
                fio, vuz_fo = exp.split('(')
                vuz, fo = vuz_fo.split(', ')
                fo = fo[:-1]
                f, i, o = fio.split()
                expert = Expert.objects.filter(last_name=f).filter(
                    first_name=i).filter(middle_name=o)
                vuz = Company.objects.get(short_name=vuz)
                expert = expert.filter(company=vuz)
                expert = expert.filter(groups=commission.group)
                if expert.count() != 1:
                    return False, exp
                else:
                    return True, expert.get()
            except:
                return False, exp
        else:
            return True, exp

    def create_dataset(myfile, commission):
        df = pd.read_excel(myfile, skiprows=2)
        check = True
        count_exp = df.shape[1]
        head = ['Заявка'] + ['Эксперт №{}'.format(i + 1) for i in range(count_exp - 1)]
        print(head)
        print(list(df))
        if head != list(df):
            print('NONE!')
            return False, None, None


        result = []
        for row in df.values:
            app = row[0]
            experts = row[1:]
            ar = []
            check_app, application = find_app(app, commission)
            if not check_app:
                check = False
            ar.append((check_app, application))

            for exp in experts:
                check_exp, expert = find_expert(exp, commission)
                if not check_exp:
                    check = False
                ar.append((check_exp, expert))
            result.append(ar)
        return check, result, head

    def load_to_bd(table):
        count = 0
        for row in table:
            app = row[0][1]
            experts = [item[1] for item in row[1:]]
            for exp in experts:
                if exp != '-':
                    c = True
                    if RelationExpertApplication.objects.filter(application=app):
                        if RelationExpertApplication.objects.filter(application=app).filter(expert=exp):
                            print('exist')
                            c = False
                    if c:
                        rel = RelationExpertApplication(expert=exp, application=app)
                        rel.save()
                        count += 1
                        print('add', rel)
        return count
    id_commission = "1"
    if 'prev' in request.POST:
        return HttpResponseRedirect('../')
    elif 'check' in request.POST or 'check_and_apply' in request.POST:
        try:
            if request.method == 'POST' and request.FILES['file']:
                myfile = request.FILES['file']
                id_commission = request.POST.get('group')

                custom_gr = CustomGroup.objects.get(group__name=dict_commission[id_commission])
                check, table, head = create_dataset(myfile, custom_gr)
                log = 'file: {}, commission: {}'.format(myfile, custom_gr.group.name)
                messages.success(request, log)
                print(table)
                if 'check' in request.POST:
                    return render(request, 'admin/load_relation.html',
                                  {'title': u'Загрузка распределения экспертов', 'check': check,
                                   'tables': table, 'head': head,
                                   'id_commission': id_commission})
                elif not check:
                    return render(request, 'admin/load_relation.html',
                                  {'title': u'Загрузка распределения экспертов', 'check': check,
                                   'tables': table, 'head': head,
                                   'id_commission': id_commission})
                else:
                    count = load_to_bd(table)
                    messages.success(request, "Успешно загружено {}".format(count))
                    return render(request, 'admin/load_relation.html',
                                  {'title': u'Загрузка распределения экспертов', 'check': check,
                                   'tables': table, 'head': head,
                                   'id_commission': id_commission})

            else:
                messages.error(request, 'Проверьте формат файла')
                return render(request, 'admin/load_relation.html',
                              {'title': u'Загрузка распределения экспертов', 'check': False,
                               'id_commission': id_commission})
        except:
            messages.error(request, 'Проверьте формат файла')
            return render(request, 'admin/load_relation.html',
                          {'title': u'Загрузка распределения экспертов', 'check': False,
                           'id_commission': id_commission})
    else:
        return render(request, 'admin/load_relation.html',
                      {'title': u'Загрузка распределения экспертов', 'check': False,
                       'id_commission': id_commission})

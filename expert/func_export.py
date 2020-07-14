import zipfile
from datetime import datetime
from sys import path
import io
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import render_to_string
from xlsxwriter import Workbook
import pandas as pd
from django.shortcuts import render
from django.contrib.auth.models import Group

from userexpert.models import Expert, CustomGroup
import transliterate
from app.models import Direction, Application
from score.models import ScoreExpertAll, ScoreCommonAll

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


def save_personal_info_to_woorksheet(workbook, worksheet, data, top_name, dop_name='Личная информация'):
    """
    Сохраняет перс. данные в красивую эксель
    """
    top_format = workbook.add_format({'bold': True, 'border': 0, 'font_name': 'Times New Roman',
                                      'align': 'left', 'font_size': 14})
    worksheet.set_column(0, 0, 30)
    worksheet.set_column(1, 30, 20)
    head_format = workbook.add_format({'bold': True, 'border': 1, 'font_name': 'Times New Roman',
                                       'align': 'center', 'valign': 'center'})
    head_format.set_align('center')
    head_format.set_align('vcenter')
    normal_text = workbook.add_format({'border': 1, 'font_name': 'Times New Roman',
                                       'align': 'left', 'valign': 'vcenter', 'text_wrap': True})
    normal_text.set_align('center')
    normal_text.set_align('vcenter')

    head = list(data)

    top = 'Экспертная комиссия "{}". {}'.format(top_name, dop_name)
    worksheet.write(0, 0, top, top_format)
    start_row = 3
    for col_num in range(len(head)):
        worksheet.write(start_row - 1, col_num, head[col_num], head_format)

    for row_num, columns in enumerate(data.values):
        for col_num, cell_data in enumerate(columns):
            worksheet.write(row_num + start_row, col_num, cell_data, normal_text)
    return worksheet


def export_personal_info_commission(commission):
    """
    По комиссии возвращает перс данные в dataframe
    """
    all_experts = Expert.objects.filter(groups__name=commission.group.name)
    head = ['Эксперт', 'Организация', 'Должность', 'Логин', 'Телефон', 'Почта']
    res = []
    for exp in all_experts:
        ar = []
        fio = '{} {} {}'.format(exp.last_name, exp.first_name, exp.middle_name)
        ar.append(fio)
        org = exp.company.short_name
        ar.append(org)
        ar.append(exp.position)
        ar.append(exp.login)
        ar.append(exp.phone)
        ar.append(exp.email)
        res.append(ar)
    df = pd.DataFrame(res, columns=head)
    return df


def export_info_for_all_com(function_info):
    """
    Собирает какие-то данные по группам, возвращает словарь
    """
    result = {}
    for comm in CustomGroup.objects.filter(admin_group=False):
        df = function_info(comm)
        result[comm] = df
    return result


def export_personal_info():
    """
    Собирает перс данные по группам, возвращает словарь
    """
    return export_info_for_all_com(export_personal_info_commission)


def export_scores_commission(commission):
    """
    По комиссии возвращает оценки в dataframe
    """
    if not commission.common_commission:
        all_directs = Direction.objects.filter(commission=commission)
        all_application = Application.objects.filter(name__in=all_directs)
        score_all = ScoreExpertAll.objects.filter(application__in=all_application)
        result = []
        head = ["Заявка", "Критерий №1", "Критерий №2", "Критерий №3", "Критерий №4", "Критерий №5", "Балл ЭК"]
        for mod in score_all:
            ar = []
            ar.append('{} - {}'.format(mod.application.name.name, mod.application.vuz.short_name))
            ar.append(mod.score1)
            ar.append(mod.score2)
            ar.append(mod.score3)
            ar.append(mod.score4)
            ar.append(mod.score5)
            ar.append(mod.score)
            result.append(ar)
        df = pd.DataFrame(result, columns=head)
        if score_all:
            df = df.sort_values(by='Балл ЭК', ascending=False)
            numbers = list(range(1, df.shape[0] + 1))
            df["№ п.п."] = numbers
            df = df[["№ п.п."] + head]
        return df
    else:
        score_all = ScoreCommonAll.objects.all()
        result = []
        head = ["Заявка", "Балл общей комиссии"]
        for mod in score_all:
            ar = []
            ar.append('{} - {}'.format(mod.application.name.name, mod.application.vuz.short_name))
            ar.append(mod.score)
            result.append(ar)
        df = pd.DataFrame(result, columns=head)
        if score_all:
            df = df.sort_values(by='Балл общей комиссии', ascending=False)
            numbers = list(range(1, df.shape[0] + 1))
            df["№ п.п."] = numbers
            df = df[["№ п.п."] + head]
        return df


def export_all_scores():
    return export_info_for_all_com(export_scores_commission)


def save_scores_to_woorksheet(workbook, worksheet, data, top_name, dop_name='Личная информация'):
    """
    Сохраняет перс. данные в красивую эксель
    """
    top_format = workbook.add_format({'bold': True, 'border': 0, 'font_name': 'Times New Roman',
                                      'align': 'left', 'font_size': 14})
    worksheet.set_column(0, 0, 10)
    worksheet.set_column(1, 1, 30)
    worksheet.set_column(2, 30, 15)
    head_format = workbook.add_format({'bold': True, 'border': 1, 'font_name': 'Times New Roman',
                                       'align': 'center', 'valign': 'center'})
    head_format.set_align('center')
    head_format.set_align('vcenter')
    normal_text = workbook.add_format({'border': 1, 'font_name': 'Times New Roman',
                                       'align': 'left', 'valign': 'vcenter', 'text_wrap': True})
    normal_text.set_align('center')
    normal_text.set_align('vcenter')

    head = list(data)

    top = 'Экспертная комиссия "{}". {}'.format(top_name, dop_name)
    worksheet.write(0, 0, top, top_format)
    start_row = 3
    for col_num in range(len(head)):
        worksheet.write(start_row - 1, col_num, head[col_num], head_format)

    for row_num, columns in enumerate(data.values):
        for col_num, cell_data in enumerate(columns):
            worksheet.write(row_num + start_row, col_num, cell_data, normal_text)
    return worksheet


def export_request(request, commission, func_for_get_data_all=export_personal_info,
                   func_for_woorksheet=save_personal_info_to_woorksheet,
                   namefile='Перс. данные', dop_name="Личная информация"):
    # func_for_get_data_all = export_personal_info
    # func_for_woorksheet = save_personal_info_to_woorksheet
    # namefile = 'Перс. данные'
    # dop_name = Личная информация

    output = io.BytesIO()
    workbook = Workbook(output, {'in_memory': True})
    result = func_for_get_data_all()

    if commission == 'all':
        for com in list(result):
            data = result[com]
            worksheet = workbook.add_worksheet(com.group.name)
            worksheet = func_for_woorksheet(workbook, worksheet, data, com.group.name, dop_name=dop_name)

    else:
        data = result[commission]
        worksheet = workbook.add_worksheet(commission.group.name)
        worksheet = func_for_woorksheet(workbook, worksheet, data, commission.group.name, dop_name=dop_name)

    workbook.close()

    date_ = '{}-{} {}-{}-{}'.format(datetime.now().hour, datetime.now().minute,
                                    datetime.now().day, datetime.now().month, datetime.now().year)
    output.seek(0)
    response = HttpResponse(output.read(),
                            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    if commission == 'all':
        rus_name = '{}_{}.xlsx'.format(namefile, date_)
    else:
        rus_name = '{}_{}_{}.xlsx'.format(namefile, commission.group.name, date_)
    filename = transliterate.translit(rus_name, reversed=True)
    response['Content-Disposition'] = "attachment; filename={}".format(filename)
    output.close()
    return response


def export_personal_info_request(request):
    """
    Страница выгрузки данных
    """
    # кнопка вернуться
    if 'prev' in request.POST:
        return HttpResponseRedirect('../')

    elif 'apply' in request.POST:
        id_ans = request.POST.get('group')
        id_what = request.POST.get('what')
        if id_what == "0":  # Выгрузка перс. данных
            if id_ans == "0":
                return export_request(request, 'all', func_for_get_data_all=export_personal_info,
                                      func_for_woorksheet=save_personal_info_to_woorksheet,
                                      namefile='Перс. данные', dop_name="Личная информация")
            else:
                name_commission = dict_commission[id_ans]
                commission = CustomGroup.objects.get(group=Group.objects.get(name=name_commission))
                return export_request(request, commission, func_for_get_data_all=export_personal_info,
                                      func_for_woorksheet=save_personal_info_to_woorksheet,
                                      namefile='Перс. данные', dop_name="Личная информация")
        elif id_what == "1":  # Распределение экспертов по заявкам # TODO
            return HttpResponseRedirect('../')
        elif id_what == "2":  # Просто результаты по комиссиям # TODO
            if id_ans == "0":
                return export_request(request, 'all', func_for_get_data_all=export_all_scores,
                                      func_for_woorksheet=save_scores_to_woorksheet,
                                      namefile='Рейтинг', dop_name="Рейтинг заяовк")
            else:
                name_commission = dict_commission[id_ans]
                commission = CustomGroup.objects.get(group=Group.objects.get(name=name_commission))
                return export_request(request, commission, func_for_get_data_all=export_all_scores,
                                      func_for_woorksheet=save_scores_to_woorksheet,
                                      namefile='Рейтинг', dop_name="Рейтинг заяовк")
        elif id_what == "3":  # Подробные результаты # TODO
            return HttpResponseRedirect('../')
        elif id_what == "4":  # Итоговые результаты # TODO
            return HttpResponseRedirect('../')


    else:
        return render(request, 'admin/export_by_commission.html',
                      {'title': u'Скачивание', })

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


def save_personal_info_to_woorksheet(workbook, worksheet, data, top_name):
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

    top = 'Экспертная комиссия "{}". {}'.format(top_name, "Личная информация")
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


def export_personal_info():
    """
    Собирает перс данные по группам, возвращает словарь
    """
    result = {}
    for comm in CustomGroup.objects.filter(admin_group=False):
        df = export_personal_info_commission(comm)
        result[comm] = df
    return result


def export_personal_info_one_com_request(request, commission):
    """
    Выгружает перс. данные по одной группе
    """
    output = io.BytesIO()
    workbook = Workbook(output, {'in_memory': True})
    data = export_personal_info_commission(commission)
    worksheet = workbook.add_worksheet(commission.group.name)
    worksheet = save_personal_info_to_woorksheet(workbook, worksheet, data, commission.group.name)

    workbook.close()
    date_ = '{}-{} {}-{}-{}'.format(datetime.now().hour, datetime.now().minute,
                                    datetime.now().day, datetime.now().month, datetime.now().year)
    output.seek(0)
    response = HttpResponse(output.read(),
                            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    rus_name = 'перс.данные_{}_{}.xlsx'.format(commission.group.name, date_)
    filename = transliterate.translit(rus_name, reversed=True)
    response['Content-Disposition'] = "attachment; filename={}".format(filename)
    output.close()
    return response


def export_personal_info_all_request(request):
    """
    Выгружает перс. данные по всем группам
    """
    output = io.BytesIO()
    result = export_personal_info()
    workbook = Workbook(output, {'in_memory': True})

    for com in list(result):
        data = result[com]
        worksheet = workbook.add_worksheet(com.group.name)
        worksheet = save_personal_info_to_woorksheet(workbook, worksheet, data, com.group.name)
    workbook.close()

    date_ = '{}-{} {}-{}-{}'.format(datetime.now().hour, datetime.now().minute,
                                    datetime.now().day, datetime.now().month, datetime.now().year)
    output.seek(0)
    response = HttpResponse(output.read(),
                            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    rus_name = 'перс.данные_все комиссии_{}.xlsx'.format(date_)
    filename = transliterate.translit(rus_name, reversed=True)
    response['Content-Disposition'] = "attachment; filename={}".format(filename)
    output.close()
    return response


def export_personal_info_request(request):
    """
    Страница выгрузки перс. данных
    """
    # кнопка вернуться
    if 'prev' in request.POST:
        return HttpResponseRedirect('../')

    elif 'apply' in request.POST:
        id_ans = request.POST.get('group')
        if id_ans == "0":
            return export_personal_info_all_request(request)
        else:
            name_commission = dict_commission[id_ans]
            commission = CustomGroup.objects.get(group=Group.objects.get(name=name_commission))
            return export_personal_info_one_com_request(request, commission)
    else:
        return render(request, 'admin/export_by_commission.html',
                      {'title': u'Скачивание', })

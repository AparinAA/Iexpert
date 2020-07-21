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
from score.models import ScoreExpert, ScoreCommon
from app.models import RelationExpertApplication
from score.models import ScoreAll
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
            try:
                worksheet.write(row_num + start_row, col_num, cell_data, normal_text)
            except TypeError:
                worksheet.write(row_num + start_row, col_num, '-', normal_text)
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
    По комиссии возвращает рейтинг в dataframe
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
    Сохраняет рейтинг заявок в красивую эксель
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
            try:
                worksheet.write(row_num + start_row, col_num, cell_data, normal_text)
            except TypeError:
                worksheet.write(row_num + start_row, col_num, '-', normal_text)
    return worksheet


def fun_for_append(ar, what):
    if not what != what:
        ar.append(what)
    else:
        ar.append('-')
    return ar


def export_detailed_scores_commission(commission):
    """
    По комиссии возвращает подробный рейтинг в dataframe
    """
    if not commission.common_commission:
        all_directs = Direction.objects.filter(commission=commission)
        all_application = Application.objects.filter(name__in=all_directs)
        score_all = ScoreExpertAll.objects.filter(application__in=all_application)
        rel_exp_sco = RelationExpertApplication.objects.filter(application__in=all_application).filter(
            common_commission=False)
        score_detail = ScoreExpert.objects.filter(relation_exp_app__in=rel_exp_sco)
        result = []
        head = ["Заявка", "Балл ЭК", "Эксперт", "Критерий №1", "Критерий №2", "Критерий №3",
                "Критерий №4", "Критерий №5", "Оценка эксперта", "Комментарий эксперта"]
        for mod in score_all:
            one_rel_exp_sco = RelationExpertApplication.objects.filter(application=mod.application).filter(
                common_commission=False)
            one_score_detail = ScoreExpert.objects.filter(relation_exp_app__in=one_rel_exp_sco)
            for sc_detail in one_score_detail:
                ar = []
                ar.append('{} - {}'.format(mod.application.name.name, mod.application.vuz.short_name))
                ar.append(mod.score)
                exp = sc_detail.relation_exp_app.expert
                fio = '{} {} {}'.format(exp.last_name, exp.first_name, exp.middle_name)
                ar.append(fio)
                ar = fun_for_append(ar, sc_detail.score1)
                ar = fun_for_append(ar, sc_detail.score2)
                ar = fun_for_append(ar, sc_detail.score3)
                ar = fun_for_append(ar, sc_detail.score4)
                ar = fun_for_append(ar, sc_detail.score5)
                ar = fun_for_append(ar, sc_detail.score)
                ar = fun_for_append(ar, sc_detail.comment)

                result.append(ar)
        df = pd.DataFrame(result, columns=head)
        return df
    else:
        score_all = ScoreCommonAll.objects.all()

        rel_exp_sco = RelationExpertApplication.objects.filter(
            common_commission=True)
        score_detail = ScoreCommon.objects.all()
        result = []
        head = ["Заявка", "Балл общей комиссии", "Эксперт", "Оценка эксперта", "Комменатрий эксперта"]
        for mod in score_all:
            one_rel_exp_sco = RelationExpertApplication.objects.filter(application=mod.application).filter(
                common_commission=True)
            one_score_detail = ScoreCommon.objects.filter(relation_exp_app__in=one_rel_exp_sco)
            for sc_detail in one_score_detail:
                ar = []
                ar.append('{} - {}'.format(mod.application.name.name, mod.application.vuz.short_name))
                ar.append(mod.score)
                exp = sc_detail.relation_exp_app.expert
                fio = '{} {} {}'.format(exp.last_name, exp.first_name, exp.middle_name)
                ar.append(fio)
                ar = fun_for_append(ar, sc_detail.score)
                ar = fun_for_append(ar, sc_detail.comment)
                result.append(ar)
        df = pd.DataFrame(result, columns=head)
        return df


def export_detailed_all_scores():
    return export_info_for_all_com(export_detailed_scores_commission)


def save_detailed_scores_to_woorksheet(workbook, worksheet, data, top_name, dop_name='Личная информация'):
    """
    Сохраняет подробный рейтинг заявок в красивую эксель
    """
    top_format = workbook.add_format({'bold': True, 'border': 0, 'font_name': 'Times New Roman',
                                      'align': 'left', 'font_size': 14})
    worksheet.set_column(0, 0, 30)
    worksheet.set_column(1, 1, 10)
    worksheet.set_column(2, 2, 20)
    worksheet.set_column(3, 30, 15)
    worksheet.set_column(9, 9, 40)
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
            try:
                worksheet.write(row_num + start_row, col_num, cell_data, normal_text)
            except TypeError:
                worksheet.write(row_num + start_row, col_num, '-', normal_text)
    return worksheet


def export_itog_scores_commission(commission):
    """
    По комиссии возвращает ИТОГОВЫЙ рейтинг в dataframe
    """
    if not commission.common_commission:
        all_directs = Direction.objects.filter(commission=commission)
        all_application = Application.objects.filter(name__in=all_directs)
        score_all = ScoreAll.objects.filter(application__in=all_application)

        result = []
        head = ["Название направления", "ВУЗ", "Балл экспертной комиссии", "Балл общей комиссии", "Итоговый балл",
                "Итоговый комментарий", "Результат"]
        for mod in score_all:
            score_all_exp = ScoreExpertAll.objects.get(application=mod.application)
            ar = []
            ar.append('{}'.format(mod.application.name.name))
            ar.append('{}'.format(mod.application.vuz.short_name))
            ar.append(mod.score_exp)
            ar.append(mod.score_com)
            ar.append(mod.score_final)
            ar.append(score_all_exp.comment_master)
            ar.append('-')
            result.append(ar)
        df = pd.DataFrame(result, columns=head)
        return df
    else:
        return pd.DataFrame()


def export_itog_all_scores():
    """
    Собирает какие-то данные по группам, возвращает словарь
    """
    result = {}
    for comm in CustomGroup.objects.filter(admin_group=False):
        if not comm.common_commission:
            df = export_itog_scores_commission(comm)
            result[comm] = df
    return result


def save_itog_scores_to_woorksheet(workbook, worksheet, data, top_name, dop_name='Личная информация'):
    """
    Сохраняет подробный рейтинг заявок в красивую эксель
    """
    top_format = workbook.add_format({'bold': True, 'border': 0, 'font_name': 'Times New Roman',
                                      'align': 'left', 'font_size': 14})
    worksheet.set_column(0, 0, 30)
    worksheet.set_column(1, 1, 10)
    worksheet.set_column(2, 30, 25)
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
            try:
                worksheet.write(row_num + start_row, col_num, cell_data, normal_text)
            except TypeError:
                worksheet.write(row_num + start_row, col_num, '-', normal_text)
    return worksheet


def export_relation_commission(commission):
    """
    По комиссии возвращает ИТОГОВЫЙ рейтинг в dataframe
    """
    if not commission.common_commission:
        all_directs = Direction.objects.filter(commission=commission)
        all_application = Application.objects.filter(name__in=all_directs)
        relation_all = RelationExpertApplication.objects.filter(application__in=all_application).filter(
            common_commission=False)

        result = []

        max_expert = 0
        for app in all_application:
            relation_all_app = RelationExpertApplication.objects.filter(application=app).filter(
                common_commission=False)
            if relation_all_app.count() > max_expert:
                max_expert = relation_all_app.count()
        head = ["Заявка"] + ["Эксперт №{}".format(i + 1) for i in range(max_expert)]
        for app in all_application:
            relation_all_app = RelationExpertApplication.objects.filter(application=app).filter(
                common_commission=False)
            ar = []
            ar.append('{} - {}'.format(app.name.name, app.vuz.short_name))
            for mod in relation_all_app:
                exp = mod.expert
                vuz = mod.expert.company.short_name
                fo = mod.expert.company.region.federal_district.short_name
                fio = '{} {} {} ({}, {})'.format(exp.last_name, exp.first_name, exp.middle_name, vuz, fo)
                ar.append(fio)
            null = ['-'] * (max_expert - relation_all_app.count())
            ar = ar + null
            result.append(ar)
        df = pd.DataFrame(result, columns=head)
        return df
    else:
        all_directs = Direction.objects.all()
        all_application = Application.objects.filter(name__in=all_directs)
        relation_all = RelationExpertApplication.objects.filter(
            common_commission=True)
        result = []

        max_expert = 0
        for app in all_application:
            relation_all_app = RelationExpertApplication.objects.filter(application=app).filter(
                common_commission=True)
            if relation_all_app.count() > max_expert:
                max_expert = relation_all_app.count()
        head = ["Заявка"] + ["Эксперт №{}".format(i + 1) for i in range(max_expert)]
        for app in all_application:
            relation_all_app = RelationExpertApplication.objects.filter(application=app).filter(
                common_commission=True)
            ar = []
            ar.append('{} - {}'.format(app.name.name, app.vuz.short_name))
            for mod in relation_all_app:
                exp = mod.expert
                vuz = mod.expert.company.short_name
                fo = mod.expert.company.region.federal_district.short_name
                fio = '{} {} {} ({}, {})'.format(exp.last_name, exp.first_name, exp.middle_name, vuz, fo)
                ar.append(fio)
            null = ['-'] * (max_expert - relation_all_app.count())
            ar = ar + null
            result.append(ar)
        df = pd.DataFrame(result, columns=head)
        return df


def export_relation():
    """
    Собирает какие-то данные по группам, возвращает словарь
    """
    return export_info_for_all_com(export_relation_commission)


def save_relation_s_to_woorksheet(workbook, worksheet, data, top_name, dop_name='Личная информация'):
    """
    Сохраняет подробный рейтинг заявок в красивую эксель
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
            try:
                worksheet.write(row_num + start_row, col_num, cell_data, normal_text)
            except TypeError:
                worksheet.write(row_num + start_row, col_num, '-', normal_text)
    return worksheet


from result.models import CheckExpertScore


def export_svod_commission(commission):
    all_expert = Expert.objects.filter(groups=commission.group)
    head = ["ФИО эксперта", "Login", "Комиссия", "Сколько заявок сделано", "Сколько заявок распрделили",
            "Закончил экспертизу (предыдущие столбцы равны)", "Подтвердил готовность оценок",
            "Организация эксперта", "ФО", "Должность", "Почта", "Телефон", "Комментарий в системе"]
    table = []
    for exp in all_expert:
        ar = []
        fio = '{} {} {}'.format(exp.last_name, exp.first_name, exp.middle_name)
        ar.append(fio)
        ar.append(exp.login)
        ar.append(commission.group.name)
        check = CheckExpertScore.objects.get(expert=exp)

        rel_exp_app = RelationExpertApplication.objects.filter(expert=exp).filter(is_active=True)
        if not commission.common_commission:
            rel_exp_app = rel_exp_app.filter(application__name__commission=commission)
        count_all = rel_exp_app.count()

        if exp.common_commission:
            exp_scores = ScoreCommon.objects.filter(relation_exp_app__in=rel_exp_app).filter(check=True)
        else:
            exp_scores = ScoreExpert.objects.filter(relation_exp_app__in=rel_exp_app).filter(check=True)
        count_ok = exp_scores.count()

        ar.append(count_ok)
        ar.append(count_all)

        ar.append('Да') if check.check_exp else ar.append('Нет')
        ar.append('Да') if count_ok == count_all else ar.append('Нет')
        ar.append(exp.company.short_name)
        ar.append(exp.company.region.federal_district.short_name)
        ar.append(exp.position)
        ar.append(exp.email)
        ar.append(exp.phone)
        ar.append(check.comment)
        table.append(ar)
    df = pd.DataFrame(table, columns=head)
    return df


def export_svod():
    """
    Собирает какие-то данные по группам, возвращает словарь
    """
    return export_info_for_all_com(export_svod_commission)


def save_svod_to_woorksheet(workbook, worksheet, data, top_name, dop_name='Личная информация'):
    """
    Сохраняет подробный рейтинг заявок в красивую эксель
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
            try:
                worksheet.write(row_num + start_row, col_num, cell_data, normal_text)
            except TypeError:
                worksheet.write(row_num + start_row, col_num, '-', normal_text)
    return worksheet


def export_request(request, commission, func_for_get_data_all=export_personal_info,
                   func_for_woorksheet=save_personal_info_to_woorksheet,
                   namefile='Перс. данные', dop_name="Личная информация", all_in_one_wheet=False):
    """
    Функция, которая выгружает красивые эксельки
    :param commission: Комиссия или 'all'
    :param func_for_get_data_all: (export_personal_info) - Функция, которая получает всю информацию в словарь датафреймов
    :param func_for_woorksheet: (save_personal_info_to_woorksheet) - Функция, которая красиво сохраняет именно этот тип данных
    :param namefile: 'Перс. данные' - название файла на русском
    :param dop_name: ' Личная информация' - Это заголовок к таблицам
    :return: response
    """

    output = io.BytesIO()
    workbook = Workbook(output, {'in_memory': True})
    result = func_for_get_data_all()

    if commission == 'all':
        if not all_in_one_wheet:
            for com in list(result):
                data = result[com]
                worksheet = workbook.add_worksheet(com.group.name)
                worksheet = func_for_woorksheet(workbook, worksheet, data, com.group.name, dop_name=dop_name)

        else:
            all_data = pd.DataFrame()
            for com in list(result):
                data = result[com]
                all_data = all_data.append(data)
            worksheet = workbook.add_worksheet("Все комиссии")
            worksheet = func_for_woorksheet(workbook, worksheet, all_data, "Все комиссии", dop_name=dop_name)
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
            if id_ans == "0":
                return export_request(request, 'all', func_for_get_data_all=export_relation,
                                      func_for_woorksheet=save_relation_s_to_woorksheet,
                                      namefile='Распределение', dop_name="Распределение экспертов")
            else:
                name_commission = dict_commission[id_ans]
                commission = CustomGroup.objects.get(group=Group.objects.get(name=name_commission))
                return export_request(request, commission, func_for_get_data_all=export_relation,
                                      func_for_woorksheet=save_relation_s_to_woorksheet,
                                      namefile='Распределение', dop_name="Распределение экспертов")
        elif id_what == "2":  # Просто результаты по комиссиям
            if id_ans == "0":
                return export_request(request, 'all', func_for_get_data_all=export_all_scores,
                                      func_for_woorksheet=save_scores_to_woorksheet,
                                      namefile='Рейтинг', dop_name="Рейтинг заявок")
            else:
                name_commission = dict_commission[id_ans]
                commission = CustomGroup.objects.get(group=Group.objects.get(name=name_commission))
                return export_request(request, commission, func_for_get_data_all=export_all_scores,
                                      func_for_woorksheet=save_scores_to_woorksheet,
                                      namefile='Рейтинг', dop_name="Рейтинг заявок")
        elif id_what == "3":  # Подробные результаты
            if id_ans == "0":
                return export_request(request, 'all', func_for_get_data_all=export_detailed_all_scores,
                                      func_for_woorksheet=save_detailed_scores_to_woorksheet,
                                      namefile='Подробный рейтинг.', dop_name="Подробный рейтинг")
            else:
                name_commission = dict_commission[id_ans]
                commission = CustomGroup.objects.get(group=Group.objects.get(name=name_commission))
                return export_request(request, commission, func_for_get_data_all=export_detailed_all_scores,
                                      func_for_woorksheet=save_detailed_scores_to_woorksheet,
                                      namefile='Подробный рейтинг.', dop_name="Подробный рейтинг")
        elif id_what == "4":  # Итоговые результаты # TODO
            if id_ans == "0":
                return export_request(request, 'all', func_for_get_data_all=export_itog_all_scores,
                                      func_for_woorksheet=save_itog_scores_to_woorksheet,
                                      namefile='Итоговый рейтинг.', dop_name="Итоговый рейтинг")
            else:
                name_commission = dict_commission[id_ans]
                commission = CustomGroup.objects.get(group=Group.objects.get(name=name_commission))
                if commission.common_commission:
                    messages.success(request, "Нельзя скачать итоговый рейтинг общей комиссии")
                    return HttpResponseRedirect("/admin/export_users/")
                else:
                    return export_request(request, commission, func_for_get_data_all=export_itog_all_scores,
                                          func_for_woorksheet=save_itog_scores_to_woorksheet,
                                          namefile='Итоговый рейтинг.', dop_name="Итоговый рейтинг")

        elif id_what == "5":  # Выгрузка сводных таблиц
            if id_ans == "0":
                return export_request(request, 'all', func_for_get_data_all=export_svod,
                                      func_for_woorksheet=save_svod_to_woorksheet,
                                      namefile='Сводная таблица',
                                      dop_name="Сводная таблица готовности работы экспертов",
                                      all_in_one_wheet=True)
            else:
                name_commission = dict_commission[id_ans]
                commission = CustomGroup.objects.get(group=Group.objects.get(name=name_commission))
                if commission.common_commission:
                    messages.success(request, "Нельзя скачать итоговый рейтинг общей комиссии")
                    return HttpResponseRedirect("/admin/export_users/")
                else:
                    return export_request(request, commission, func_for_get_data_all=export_svod,
                                          func_for_woorksheet=save_svod_to_woorksheet,
                                          namefile='Сводная таблица',
                                          dop_name="Сводная таблица готовности работы экспертов",
                                          all_in_one_wheet=True)
    else:
        return render(request, 'admin/export_by_commission.html',
                      {'title': u'Скачивание', })

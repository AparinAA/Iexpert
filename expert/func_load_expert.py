import sys
import zipfile
from datetime import datetime
from sys import path
import io
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import render_to_string
from django.template.response import TemplateResponse, SimpleTemplateResponse
from xlsxwriter import Workbook
import pandas as pd
import tablib
import transliterate
from django.contrib.auth.base_user import BaseUserManager
from django.http import HttpResponse, HttpResponseRedirect
import pandas as pd
from django.shortcuts import render
from django.contrib.auth.models import Group
from userexpert.models import Expert, CustomGroup
from app.models import Application, Direction, RelationExpertApplication
from info.models import Company
from django.contrib import messages
from django.core.validators import validate_email

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
from django.core.validators import validate_email
from django.core.exceptions import ValidationError


def func_load_expert(request):
    def clear_word(word, zn=True):
        if word != word:
            return '-'
        word = str(word)
        if zn:
            word = word.replace('.', '. ')
        while word.find('  ') != -1:
            word = word.replace('  ', ' ')
        while word[-1] == ' ':
            word = word[:-1]
        while word[0] == ' ':
            word = word[1:]

        return word

    def find_next_login(osnova='expert', last_num=1):
        i = 0
        set_login = set()
        for val in Expert.objects.all().values('login'):
            set_login.add(val['login'])
        while True:
            log = '{}{}'.format(osnova, last_num + i)
            if log not in set_login:
                return log, i
            i += 1

    def load_to_bd(table, save=False):
        new_table = []
        # Загружает в БД
        count = 0
        for row in table:
            ar = []
            data_row = [item[1] for item in row]
            f, i, o, gender, commissions, work, possition, fo, phone, email, comment = data_row[1:]
            exp = Expert.objects.filter(last_name=f).filter(first_name=i).filter(middle_name=o)
            last_num = 1
            if exp.count() == 0:
                ar.append(('green', 'add new'))
                log, last_num_b = find_next_login(osnova='expert', last_num=last_num)
                last_num += last_num_b
                password = BaseUserManager().make_random_password(length=8)
                ar.append(('green', log))
                ar.append(('green', password))
                if save:
                    exp = Expert.objects.create_user(log, password=password)
                    exp.last_name = f
                    exp.first_name = i
                    exp.middle_name = o

                for it in (f, i, o):
                    ar.append(('green', it))

                if gender.lower() == 'м':
                    ar.append(('green', 'м'))
                    if save:
                        exp.gender = 'm'
                else:
                    ar.append(('green', 'ж'))
                    if save:
                        exp.gender = 'f'

                for com in commissions.split(', '):
                    cl_com = clear_word(com)
                    gr = Group.objects.get(name=cl_com)
                    if save:
                        gr.user_set.add(exp)

                ar.append(('green', commissions))
                try:
                    company1 = Company.objects.filter(short_name=work.short_name)
                    company2 = Company.objects.filter(full_name=work.full_name)
                    company = company1 | company2
                except:
                    work = clear_word(work)
                    company1 = Company.objects.filter(short_name=work)
                    company2 = Company.objects.filter(full_name=work)
                    company = company1 | company2

                ar.append(('green', company.get()))

                if save:
                    exp.company = company.get()
                    exp.position = clear_word(possition)
                    exp.phone = clear_word(phone)
                    exp.email = clear_word(email)
                    exp.comment = clear_word(comment)
                    exp.save()

                for it in [possition, fo, phone, email, comment]:
                    ar.append(('green', clear_word(it)))
                count += 1
                new_table.append(ar)

            else:
                ar = []
                ar.append(('orange', 'not new expert'))
                ar.append(('orange', exp.get().login))
                ar.append(('orange', '-'))
                for it in f, i, o, gender, commissions, work, possition, fo, phone, email, comment:
                    ar.append(('orange', it))
                new_table.append(ar)
        return new_table, count

    def create_dataset(myfile):
        # Создает табличку для html
        df = pd.read_excel(myfile)
        check = True
        count = df.shape[0]
        head = ['Фамилия', 'Имя', 'Отчество', 'Пол', 'Комиссия', 'Место работы', 'Должность', 'ФО', 'Телефон', 'Почта',
                'Примечание']
        for el in head:
            if el not in list(df):
                messages.error(request, 'Нет нужных столбцов')
                return False, None, None, 0

        result = []
        for row in df[head].values:
            f, i, o, gender, commissions, work, possition, fo, phone, email, comment = row
            f, i, o = clear_word(f), clear_word(i), clear_word(o)
            commissions = clear_word(commissions)
            ar = []
            check_exp = 'green'
            exp = Expert.objects.filter(last_name=f).filter(first_name=i).filter(middle_name=o)
            if exp.count() != 0:
                check_exp = 'orange'
                ar.append((check_exp, 'not new expert'))
            else:
                ar.append((check_exp, 'new expert'))

            ar.append((check_exp, f))
            ar.append((check_exp, i))
            ar.append((check_exp, o))
            ch = 'green'
            for com in commissions.split(', '):
                cl_com = clear_word(com)
                gr = Group.objects.filter(name=cl_com)
                if gr.count() == 0:
                    ch = 'red'
                    check = False
            if gender.lower() in ('м', 'ж'):
                ar.append(('green', gender))
            else:
                check = False
                ar.append(('red', gender))
            ar.append((ch, commissions))

            work = clear_word(work)
            company1 = Company.objects.filter(short_name=work)
            company2 = Company.objects.filter(full_name=work)
            company = company1 | company2
            if company.count() != 1:
                check = False
                ar.append(('red', work))
            else:
                ar.append(('green', company.get()))

            i = 0
            for it in [possition, fo, phone, email, comment]:
                if i == 3:
                    it_cl = clear_word(str(it), zn=False)
                    try:
                        validate_email(it_cl)
                        ar.append(('green', it_cl))
                    except ValidationError:
                        ar.append(('red', it_cl))
                        check = False
                    except:
                        ar.append(('red', it_cl))
                        check = False
                else:
                    if it != it:
                        ar.append(('gray', '-'))
                    else:
                        it_cl = clear_word(str(it))
                        ar.append(('gray', it_cl))
                i += 1
            result.append(ar)
        head = [''] + head
        return check, result, head, count

    def return_df(table, head):
        data = pd.DataFrame(table, columns=head)
        output = io.BytesIO()
        date_ = '{}-{} {}-{}-{}'.format(datetime.now().hour, datetime.now().minute,
                                        datetime.now().day, datetime.now().month, datetime.now().year)
        workbook = Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet(date_)

        worksheet.set_column(0, 6, 20)
        worksheet.set_column(7, 40, 40)
        worksheet.set_column(9, 9, 10)
        worksheet.set_column(8, 8, 50)

        head_format = workbook.add_format({'bold': True, 'border': 1, 'font_name': 'Times New Roman',
                                           'align': 'center', 'valign': 'center'})
        head_format.set_align('center')
        head_format.set_align('vcenter')

        normal_text_green = workbook.add_format({'border': 1, 'font_name': 'Times New Roman',
                                                 'align': 'left', 'valign': 'vcenter', 'text_wrap': True})
        normal_text_green.set_align('left')
        normal_text_green.set_align('vcenter')
        normal_text_green.set_bg_color('#90EE90')

        normal_text_orange = workbook.add_format({'border': 1, 'font_name': 'Times New Roman',
                                                  'align': 'left', 'valign': 'vcenter', 'text_wrap': True})
        normal_text_orange.set_align('left')
        normal_text_orange.set_align('vcenter')
        normal_text_orange.set_bg_color('#FFAC46')

        start_row = 0
        for col, it in enumerate(head):
            worksheet.write(start_row, col, it, head_format)
        start_row += 1
        for row_num, columns in enumerate(data.values):
            for col_num, cell_data in enumerate(columns):
                if cell_data[0] == 'orange':
                    worksheet.write(row_num + start_row, col_num, str(cell_data[1]), normal_text_orange)
                else:
                    worksheet.write(row_num + start_row, col_num, str(cell_data[1]), normal_text_green)
        workbook.close()

        output.seek(0)
        content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        response = HttpResponse(output.read(), content_type=content_type)
        rus_name = '{}_{}.xlsx'.format('Загруженные эксперты', date_)
        filename = transliterate.translit(rus_name, reversed=True)
        response['Content-Disposition'] = "attachment; filename={}".format(filename)
        output.close()
        return response

    if 'prev' in request.POST:
        return HttpResponseRedirect('../')
    if 'company' in request.POST:
        return HttpResponseRedirect('../info/company/')
    elif 'check' in request.POST or 'check_and_apply' in request.POST:
        try:
            if request.method == 'POST' and request.FILES['file']:
                myfile = request.FILES['file']
                check, table, head, count = create_dataset(myfile)
                log = 'file: {}, count: {}'.format(myfile, count)
                if check:
                    messages.success(request, log)
                    if 'check' in request.POST:
                        temp = 'admin/load_expert.html'
                        dict_ = {'title': u'Загрузка экспертов', 'check': check,
                                 'tables': table, 'head': head,
                                 }
                        return render(request, temp, dict_)
                    else:
                        table, count = load_to_bd(table, save=True)
                        head = ['', 'login', 'password'] + head[1:]
                        if count == 0:
                            return render(request, 'admin/load_expert.html',
                                          {'title': u'Загрузка экспертов', 'check': check,
                                           'tables': table, 'head': head,
                                           })
                        else:
                            messages.success(request, "Успешно загружено {}".format(count))
                            return return_df(table, head)
                else:
                    messages.error(request, log)
                    return render(request, 'admin/load_expert.html',
                                  {'title': u'Загрузка экспертов', 'check': check,
                                   'tables': table, 'head': head,
                                   })



        except:
            log = "Unexpected error: {}".format(sys.exc_info())
            messages.error(request, log)
            return render(request, 'admin/load_expert.html',
                          {'title': u'Загрузка экспертов', 'check': False,
                           'tables': None, 'head': None,
                           })

    else:
        return render(request, 'admin/load_expert.html',
                      {'title': u'Загрузка экспертов', 'check': False,
                       })

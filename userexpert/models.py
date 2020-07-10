from datetime import datetime

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from info.models import Company


class MyUserManager(BaseUserManager):
    def create_user(self, login, password=None, **kwargs):
        if not login:
            raise ValueError('У пользователей должен быть логин')
        if not password:
            raise ValueError('У пользователей должен быть пароль')

        user = self.model(
            login=login,
            date_joined=datetime.today(),
            # common_commission=False,
            # master_group=False,
            **kwargs
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, login, password=None, **kwargs):
        user = self.create_user(
            login,
            password=password,
            # common_commission=False,
            # master_group=False,
            **kwargs
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class Expert(AbstractBaseUser, PermissionsMixin):
    login = models.CharField(verbose_name='Логин пользователя', max_length=100, unique=True)
    email = models.EmailField(verbose_name='Электронная почта', max_length=255)
    is_active = models.BooleanField(default=True, verbose_name='Активная запись')
    is_admin = models.BooleanField(default=False, verbose_name='Админ')

    first_name = models.CharField(verbose_name='Имя', max_length=100)
    middle_name = models.CharField(verbose_name='Отчество', max_length=100)
    last_name = models.CharField(verbose_name='Фамилия', max_length=100)
    date_joined = models.DateField(verbose_name='Дата регистрации')

    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name='Вуз/Организация', null=True)

    position = models.CharField(verbose_name='Должность', max_length=200)
    phone = models.CharField(blank=True, null=True, verbose_name='Телефон', max_length=20)
    common_commission = models.BooleanField(verbose_name='Общая комиссия', default=False)
    expert_commission = models.BooleanField(verbose_name='Общая комиссия', default=True)
    master_group = models.BooleanField(verbose_name='Ответственный секретарь', default=False)
    objects = MyUserManager()

    USERNAME_FIELD = 'login'
    REQUIRED_FIELDS = []  # 'last_name', 'first_name', 'middle_name', ]

    def __str__(self):
        s = '{} {} {}'.format(self.last_name, self.first_name, self.middle_name)
        return s

    @property
    def is_staff(self):
        return self.is_admin

    def has_perm(self, perm, obj=None):
        if self.is_staff:
            return True
        if perm in self.get_all_permissions():
            return True
        else:
            return False

    def has_perms_or(self, perm_list):
        # Функция, которая возвращает нам есть ли хотя бы одни такие права (нужна в очень редких случаях)
        check = False
        for perm in perm_list:
            check = check or self.has_perm(perm)
        return check

    def has_module_perms(self, app_label):
        return self.is_admin

    class Meta:
        verbose_name = 'Эксперт'
        verbose_name_plural = 'Эксперты'
        ordering = ['last_name', 'first_name', 'middle_name']
        # unique_together = ('last_name', 'first_name', 'middle_name')

    @property
    def is_common_commission(self):  # Отвечает на вопрос состоит ли эксперт в общей комиссии
        try:
            all_commissions = self.groups.all()
            if all_commissions:
                for group in all_commissions:
                    cg = CustomGroup.objects.get(group=group)
                    if cg.common_commission:
                        return True
            return False
        except:
            return False

    @property
    def is_master_group(self):
        try:
            all_commissions = self.groups.all()
            for group in all_commissions:
                cg = CustomGroup.objects.get(group=group)
                if cg.master == self:
                    return True
            return False
        except:
            return False

    def save(self, *args, **kwargs):
        try:
            if self.is_common_commission:
                self.common_commission = True
            else:
                self.common_commission = False
            if self.is_master_group:
                self.master_group = True
            else:
                self.master_group = False
            print(self.groups, self.common_commission)
        except:
            pass
        super(Expert, self).save(*args, **kwargs)

    @property
    def get_commission(self):  # Отдает список групп эксперта
        return self.groups.all()

    @property
    def get_custom_commission(self):  # Отдает список групп эксперта
        all_gr = []
        for gr in self.groups.all():
            all_gr.append(gr)
        cg = CustomGroup.objects.all().filter(group__in=all_gr)
        return cg

    @property
    def get_commission_master(self):  # Отдает список групп эксперта
        if self.master_group:
            com = CustomGroup.objects.all().get(master=self)
            return com
        else:
            return None

    def get_commissions(self):  # Отдает список групп эксперта
        return self.groups.all()

    def get_absolute_url(self):  # new
        # return reverse('expert-detail', args=[str(self.id)])
        return reverse('index')


from django.db import models


class CustomGroup(models.Model):
    group = models.OneToOneField('auth.Group', unique=True, on_delete=models.CASCADE)
    master = models.ForeignKey(Expert, verbose_name='Ответственный секретарь', blank=True,
                               null=True, on_delete=models.CASCADE, related_name='+')

    common_commission = models.BooleanField(default=False, verbose_name='Общая комиссия')
    admin_group = models.BooleanField(default=False, verbose_name='Группа администраторов')

    def __str__(self):
        return "{}".format(self.group.name)

    class Meta:
        verbose_name_plural = "Комиссии"
        verbose_name = "Комиссия"

    def name(self):
        return self.group.name

    def permissions(self):
        return self.group.permissions.all()

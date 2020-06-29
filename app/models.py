from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from info.models import Company
from userexpert.models import Expert, CustomGroup


class Direction(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название направления')
    commission = models.ForeignKey(CustomGroup, verbose_name='Экспертная комиссия',
                                   on_delete=models.CASCADE, default=None,
                                   limit_choices_to=Q(admin_group=False) & Q(common_commission=False),
                                   # limit_choices_to={'admin_group': False}
                                   )

    class Meta:
        verbose_name_plural = "Направления"
        verbose_name = "Направление"
        ordering = ['name']

    def __str__(self):
        return self.name


class Application(models.Model):
    def get_limit_choices_to(self):
        return True

    id = models.AutoField(primary_key=True)
    name = models.ForeignKey(Direction, verbose_name='Направление', on_delete=models.CASCADE,
                             default=None)
    vuz = models.ForeignKey(Company, verbose_name='ВУЗ', on_delete=models.CASCADE,
                            limit_choices_to={'is_vuz': True},
                            default=None)
    link_archiv = models.URLField(verbose_name='Ссылка на архив', blank=True)

    class Meta:
        verbose_name_plural = "Заявки"
        verbose_name = "Заявка"
        ordering = ['name']

    def __str__(self):
        return '{} - {}'.format(self.name, self.vuz.short_name)

    def get_absolute_url(self):
        return reverse('application-detail', args=[str(self.id)])

    @property
    def get_group(self):
        return self.name.commission.group

    @property
    def get_commission(self):
        return self.name.commission


class RelationExpertApplication(models.Model):
    expert = models.ForeignKey(Expert,
                               related_name='rel_exp_app',
                               on_delete=models.CASCADE,
                               verbose_name='Эксперт',
                               default=None)
    application = models.ForeignKey(Application,
                                    related_name='rel_exp_app',
                                    on_delete=models.CASCADE,
                                    verbose_name='Заявка',
                                    default=None)
    common_commission = models.BooleanField(verbose_name='Общая комиссия',
                                            default=False)
    is_active = models.BooleanField(verbose_name='Активное распределение', default=True)

    class Meta:
        verbose_name_plural = 'Связи экспертов и заявок'
        verbose_name = 'Связь эксперта с заявкой'
        unique_together = ('expert', 'application')

    def __str__(self):
        return '{} - {} - {}'.format(self.expert, self.application.name, self.application.vuz.short_name)

    def clean(self, *args, **kwargs):
        super(RelationExpertApplication, self).clean(*args, **kwargs)
        if self.application is None and self.expert is None:
            raise ValidationError("Все поля должны быть заполнены")
        expert = self.expert
        relation_exp = Expert.objects.all().get(pk=expert.id).get_commissions()
        if not Expert.objects.all().get(pk=expert.id).is_common_commission:
            if self.application.name.commission.group not in relation_exp:
                raise ValidationError(_('Заявка из комиссии: {}. Эксперт состоит в комиссиях: {}'.format(
                    self.application.name.commission,
                    relation_exp)))
            if self.application.name.commission.admin_group:
                raise ValidationError(_('Нельзя добавить заявку в админскую группу'))

    def save(self, *args, **kwargs):
        self.full_clean()
        self.common_commission = self.get_type_commission()
        super(RelationExpertApplication, self).save(*args, **kwargs)

    def get_type_commission(self):
        expert = self.expert
        return Expert.objects.all().get(pk=expert.id).is_common_commission

    def get_commissions(self):  # TODO ПРОВЕРИТЬ
        expert = self.expert
        all_commissions = expert.get_commissions()
        if expert.is_common_commission:
            for commission in all_commissions:
                if commission.common_commission:
                    return commission
        else:
            return self.application.name.commision

    def get_application(self):  # TODO ПРОВЕРИТЬ
        return self.application

    def get_expert(self):  # TODO ПРОВЕРИТЬ
        return self.expert
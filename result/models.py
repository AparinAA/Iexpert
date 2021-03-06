from django.urls import reverse
from datetime import datetime

from django.db import models

# Create your models here.
from django.http import HttpResponseRedirect

from app.models import RelationExpertApplication, Direction, Application
from score.models import ScoreExpert, ScoreCommon, ScoreExpertAll, ScoreCommonAll
from userexpert.models import Expert, CustomGroup



class CheckExpertScore(models.Model):
    expert = models.ForeignKey(Expert, verbose_name='Эксперт',
                               on_delete=models.CASCADE, default=None, )
    check_exp = models.BooleanField(default=False, verbose_name='Готовность Эксперта')

    count_all = models.IntegerField(default=0, verbose_name='Кол-во назначенных заявок')

    count_ok = models.IntegerField(default=0, verbose_name='Кол-во готовых заявок')

    date_last = models.DateField(default=None, verbose_name='Последнее обновление', null=True, blank=True)

    comment = models.TextField(max_length=2000, verbose_name='Комметарий по эксперту', null=True, blank=True)

    def __str__(self):
        return '{} {} {}'.format(self.expert.last_name, self.expert.first_name, self.expert.middle_name)

    class Meta:
        verbose_name_plural = 'Готовность оценок по эксперту'
        verbose_name = 'Готовность оценок по эксперту'

    def save(self, *args, **kwargs):
        self.full_clean()
        self.date_last = datetime.now(tz=None)
        rel_exp_app = RelationExpertApplication.objects.all().filter(expert=self.expert).filter(is_active=True)
        self.count_all = rel_exp_app.count()
        if self.expert.common_commission:
            exp_scores = ScoreCommon.objects.filter(relation_exp_app__in=rel_exp_app).filter(check=True)
        else:
            exp_scores = ScoreExpert.objects.filter(relation_exp_app__in=rel_exp_app).filter(check=True)
        self.count_ok = exp_scores.count()
        super(CheckExpertScore, self).save(*args, **kwargs)

    @property
    def get_all_score(self):
        rel_exp_app = RelationExpertApplication.objects.all().filter(expert=self.expert).filter(is_active=True)
        exp_scores = ScoreExpert.objects.filter(relation_exp_app__in=rel_exp_app).order_by('relation_exp_app__application__name__name',
                                                                                           'relation_exp_app__application__vuz__short_name')
        self.save()
        return exp_scores

    @property
    def get_all_score_common(self):
        rel_exp_app = RelationExpertApplication.objects.all().filter(expert=self.expert).filter(is_active=True)
        exp_scores = ScoreCommon.objects.filter(relation_exp_app__in=rel_exp_app).order_by('relation_exp_app__application__name__name',
                                                                                           'relation_exp_app__application__vuz__short_name')
        self.save()
        return exp_scores

    def get_absolute_url(self):
        return reverse('all_score_for_expert_form', args=[str(self.id)])


class ResultMaster(models.Model):
    STATUS_CHOICES = (('b', 'Начальный статус'),
                      ('r', 'Может смотреть распределение'),
                      ('w', 'Может писать комментарии'))

    master = models.ForeignKey(Expert, verbose_name='Ответственный секретарь',
                               on_delete=models.CASCADE, default=None, limit_choices_to={'master_group': True}, )
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default='b', verbose_name='Статус доступа')

    check = models.BooleanField(default=False, verbose_name='Готовность ответственного секретаря')

    count_all = models.IntegerField(default=0, verbose_name='Кол-во всего заявок')

    count_ok = models.IntegerField(default=0, verbose_name='Кол-во готовых комментариев')

    date_last = models.DateField(default=None, verbose_name='Последнее обновление', null=True, blank=True)

    comment = models.TextField(max_length=2000, verbose_name='Любое примичание', null=True, blank=True)

    def __str__(self):
        return '{} {} {}'.format(self.master.last_name, self.master.first_name, self.master.middle_name)

    class Meta:
        verbose_name_plural = 'Готовность ответственных секретарей'
        verbose_name = 'Готовность ответственных секретарей'

    def save(self, *args, **kwargs):
        self.full_clean()
        self.date_last = datetime.now(tz=None)
        commission = self.master.get_commission_master
        if self.master.common_commission:
            all_app = Application.objects.all()
            scores = ScoreCommonAll.objects.all()
            self.count_all = scores.count()
            self.count_ok = scores.filter(check=True).count()
        else:
            all_app = Application.objects.filter(name__commission=commission)
            scores = ScoreExpertAll.objects.filter(application__in=all_app)
            self.count_all = scores.count()
            self.count_ok = scores.filter(check=True).count()
        super(ResultMaster, self).save(*args, **kwargs)

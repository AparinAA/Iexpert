from django.urls import reverse
from datetime import datetime

from django.db import models

# Create your models here.
from django.http import HttpResponseRedirect

from app.models import RelationExpertApplication, Direction, Application
from score.models import ScoreExpert, ScoreCommon
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
        verbose_name_plural = 'Готовность оценок по эксперта'
        verbose_name = 'Готовность оценок по эксперта'

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
        exp_scores = ScoreExpert.objects.filter(relation_exp_app__in=rel_exp_app)
        self.save()
        return exp_scores

    @property
    def get_all_score_common(self):
        rel_exp_app = RelationExpertApplication.objects.all().filter(expert=self.expert).filter(is_active=True)
        exp_scores = ScoreCommon.objects.filter(relation_exp_app__in=rel_exp_app)
        self.save()
        return exp_scores

    def get_absolute_url(self):
        return reverse('all_score_for_expert_form', args=[str(self.id)])


class CheckGroups(models.Model):
    commission = models.ForeignKey(CustomGroup, verbose_name='Комиссия',
                                   on_delete=models.CASCADE, default=None, )
    check_group = models.BooleanField(default=False, verbose_name='Готовность комиссии')

    count_app_all = models.IntegerField(default=0, verbose_name='Кол-во назначенных заявок')

    count_app_ok = models.IntegerField(default=0, verbose_name='Кол-во готовых заявок')

    count_exp_all = models.IntegerField(default=0, verbose_name='Кол-во рабочих экспертов')

    count_exp_ok = models.IntegerField(default=0, verbose_name='Кол-во готовых экспертов')

    date_last = models.DateField(default=None, verbose_name='Последнее обновление', null=True, blank=True)

    comment = models.TextField(max_length=2000, verbose_name='Комметарий по эксперту', null=True, blank=True)

    def __str__(self):
        return '{}'.format(self.commission.group.name)

    class Meta:
        verbose_name_plural = 'Готовность по группам'
        verbose_name = 'Готовность по группам'

    def save(self, *args, **kwargs):
        self.full_clean()
        self.date_last = datetime.now(tz=None)
        all_expert_commission = Expert.objects.all().filter(groups=self.commission.group)
        rel_exp_app = CheckExpertScore.objects.all().filter(expert__in=all_expert_commission)
        self.count_exp_all = rel_exp_app.count()
        exp_scores = rel_exp_app.filter(check_exp=True)
        self.count_exp_ok = exp_scores.count()

        all_direct = Direction.objects.all().filter(commission=self.commission)
        all_app = Application.objects.all().filter(name__in=all_direct)
        print(all_app)
        self.count_app_all = all_app.count()
        all_score_exp = ScoreExpert.objects.filter()
        self.count_app_ok = 0  # TODO
        super(CheckGroups, self).save(*args, **kwargs)


class CheckApplication(models.Model):
    application = models.ForeignKey(Application, verbose_name='Заявка',
                                    on_delete=models.CASCADE, default=None, )
    check_app = models.BooleanField(default=False, verbose_name='Готовность заявки')

    count_exp_all = models.IntegerField(default=0, verbose_name='Кол-во рабочих экспертов')

    count_exp_ok = models.IntegerField(default=0, verbose_name='Кол-во готовых экспертов')

    date_last = models.DateField(default=None, verbose_name='Последнее обновление', null=True, blank=True)

    comment = models.TextField(max_length=2000, verbose_name='Комметарий по эксперту', null=True, blank=True)

    def __str__(self):
        return '{}'.format(self.commission.group.name)

    class Meta:
        verbose_name_plural = 'Готовность по заявкам'
        verbose_name = 'Готовность по заявкам'

    def save(self, *args, **kwargs):
        self.full_clean()
        self.date_last = datetime.now(tz=None)
        # TODO надо обновить count_exp_all and count_exp_ok
        super(CheckApplication, self).save(*args, **kwargs)

from django.db import models
from django.urls import reverse
from django.utils.safestring import mark_safe

from app.models import Application, RelationExpertApplication
from score.function_score import scalar_product_exp_scores, mean_any, MyError, scalar_product_com_exp
import json
from datetime import datetime
import os
# Create your models here.

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class ScoreCommon(models.Model):
    """
    Оценки общей комиссии в связке с экспертами и заявками (самая подробная информация)
    """
    with open(os.path.join(BASE_DIR , 'score/info.json'), 'r', encoding='utf-8') as file:
        data_score = json.load(file)
    can_score = ((1, 1), (2, 2), (3, 3), (4, 4), (5, 5),
                 (6, 6), (7, 7), (8, 8), (9, 9), (10, 10))
    relation_exp_app = models.ForeignKey(RelationExpertApplication,
                                         verbose_name='Эксперт - заявка',
                                         on_delete=models.CASCADE, default=None,
                                         limit_choices_to={'common_commission': True}
                                         )
    score = models.IntegerField(default=None, verbose_name='Оценка',
                                choices=can_score, blank=True, null=True,
                                help_text=mark_safe(data_score['common']['score'])
                                )
    comment = models.TextField(default=None, verbose_name='Комментарий по заявке',
                               blank=True, null=True,
                               max_length=1000,
                               help_text=mark_safe(data_score['common']['comment'])
                               )
    check = models.BooleanField(default=False, verbose_name='Готово')
    is_active = models.BooleanField(default=True, verbose_name='Активное')

    date_last = models.DateField(default=None, verbose_name='Последнее обновление', null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Оценки экспертов ОК по заявке'
        verbose_name = 'Оценка эксперта ОК по заявке'

    def get_absolute_url(self):
        return reverse('score_common_detail', args=[str(self.id)])

    def __str__(self):
        return self.relation_exp_app.__str__()

    def save(self, *args, **kwargs):
        self.full_clean()
        if not (self.score is None or self.comment is None or len(self.comment) == 0):
            self.check = True
        else:
            self.check = False
        self.date_last = datetime.now(tz=None)
        rel = RelationExpertApplication.objects.get(id=self.relation_exp_app.id)
        self.is_active = rel.is_active
        super(ScoreCommon, self).save(*args, **kwargs)


class ScoreExpert(models.Model):
    """
    Оценки общей комиссии в связке с экспертами и заявками (самая подробная информация)
    """
    with open(os.path.join(BASE_DIR , 'score/info.json'), 'r', encoding='utf-8') as file:
        data_score = json.load(file)
    can_score = ((1, 1), (2, 2), (3, 3), (4, 4), (5, 5),
                 (6, 6), (7, 7), (8, 8), (9, 9), (10, 10))
    relation_exp_app = models.ForeignKey(RelationExpertApplication,
                                         verbose_name='Эксперт - заявка',
                                         on_delete=models.CASCADE, default=None,
                                         limit_choices_to={'common_commission': False}
                                         )
    score1 = models.IntegerField(default=None, verbose_name='Критерий №1',
                                 choices=can_score, blank=True, null=True,
                                 help_text=mark_safe(data_score['expert']['score1'])
                                 )
    score2 = models.IntegerField(default=None, verbose_name='Критерий №2',
                                 choices=can_score, blank=True, null=True,
                                 help_text=mark_safe(data_score['expert']['score2'])
                                 )
    score3 = models.IntegerField(default=None, verbose_name='Критерий №3',
                                 choices=can_score, blank=True, null=True,
                                 help_text=mark_safe(data_score['expert']['score3'])
                                 )
    score4 = models.IntegerField(default=None, verbose_name='Критерий №4',
                                 choices=can_score, blank=True, null=True,
                                 help_text=mark_safe(data_score['expert']['score4'])
                                 )
    score5 = models.IntegerField(default=None, verbose_name='Критерий №5',
                                 choices=can_score, blank=True, null=True,
                                 help_text=mark_safe(data_score['expert']['score5'])
                                 )
    score = models.FloatField(default=None, verbose_name='Оценка эксперта',
                              blank=True, null=True)

    comment = models.TextField(default=None, verbose_name='Комментарий по заявке',
                               max_length=1000, blank=True, null=True,
                               help_text=mark_safe(data_score['expert']['comment'])
                               )
    check = models.BooleanField(default=False, verbose_name='Готово')
    is_active = models.BooleanField(default=True, verbose_name='Активное')
    date_last = models.DateField(default=None, verbose_name='Последнее обновление', null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Оценки экспертов ЭК по заявке'
        verbose_name = 'Оценка эксперта ЭК по заявке'

    def get_absolute_url(self):
        return reverse('score_expert_detail', args=[str(self.id)])

    def save(self, *args, **kwargs):
        self.full_clean()
        if (not self.score1 is None) and (not self.score2 is None) and (
                not self.score3 is None) and (not self.score4 is None) and (
                not self.score5 is None):
            self.score = scalar_product_exp_scores([self.score1, self.score2, self.score3, self.score4, self.score5])
            if not (self.comment is None or len(self.comment) == 0):
                self.check = True
            else:
                self.check = False
        else:
            self.check = False
            self.score = None
        self.date_last = datetime.now(tz=None)
        rel = RelationExpertApplication.objects.get(id=self.relation_exp_app.id)
        self.is_active = rel.is_active
        super(ScoreExpert, self).save(*args, **kwargs)


class ScoreCommonAll(models.Model):
    """
    Оценки общей комиссии по заявкам (Уже средние)
    """
    application = models.ForeignKey(Application, verbose_name='Заявка',
                                    on_delete=models.CASCADE, default=None, )
    score = models.FloatField(default=None, verbose_name='Оценка заявки',
                              blank=True, null=True)
    comment_master = models.TextField(default=None, verbose_name='Комментарий ответственного секретаря',
                                      max_length=2000, blank=True, null=True
                                      )
    check = models.BooleanField(default=False, verbose_name='Готово')
    date_last = models.DateField(default=None, verbose_name='Последнее обновление', null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Все оценки ОК по заявке'
        verbose_name = 'Все оценки ОК по заявке'

    def get_absolute_url(self):
        return reverse('score_common_all_detail', args=[str(self.id)])

    def __str__(self):
        return self.application.__str__()

    @property
    def get_all_comments_and_scores(self):
        rel_exp_app = RelationExpertApplication.objects.all().filter(application=self.application).filter(
            common_commission=True).filter(is_active=True)
        scores_common = ScoreCommon.objects.all().filter(relation_exp_app__in=rel_exp_app)
        dict_all = {}
        for sc in scores_common:
            dict_all[sc.relation_exp_app.expert] = {}
            dict_all[sc.relation_exp_app.expert]['comment'] = sc.comment
            dict_all[sc.relation_exp_app.expert]['score'] = sc.score
        return dict_all

    def save(self, *args, **kwargs):
        self.full_clean()
        rel_exp_app = RelationExpertApplication.objects.all().filter(application=self.application).filter(
            common_commission=True).filter(is_active=True)
        scores_common = ScoreCommon.objects.all().filter(relation_exp_app__in=rel_exp_app)
        comments = []
        scores = []
        for sc in scores_common:
            comments.append(sc.comment)
            scores.append(sc.score)
        try:
            self.score = mean_any(scores)
        except MyError:
            print('not found socres')
        if not (self.score is None or self.comment_master is None or len(self.comment_master) == 0):
            self.check = True
        else:
            self.check = False
        self.date_last = datetime.now(tz=None)
        super(ScoreCommonAll, self).save(*args, **kwargs)


class ScoreExpertAll(models.Model):
    """
    Оценки экспертных комиссий по заявкам (Уже средние)
    """
    application = models.ForeignKey(Application, verbose_name='Заявка',
                                    on_delete=models.CASCADE, default=None, )
    score1 = models.FloatField(default=None, verbose_name='Критерий №1',
                               blank=True, null=True
                               )
    score2 = models.FloatField(default=None, verbose_name='Критерий №2',
                               blank=True, null=True
                               )
    score3 = models.FloatField(default=None, verbose_name='Критерий №3',
                               blank=True, null=True
                               )
    score4 = models.FloatField(default=None, verbose_name='Критерий №4',
                               blank=True, null=True
                               )
    score5 = models.FloatField(default=None, verbose_name='Критерий №5',
                               blank=True, null=True
                               )
    score = models.FloatField(default=None, verbose_name='Оценка заявки',
                              blank=True, null=True)
    comment_master = models.TextField(default=None, verbose_name='Комментарий ответственного секретаря',
                                      max_length=2000, blank=True, null=True
                                      )
    check = models.BooleanField(default=False, verbose_name='Готово')
    date_last = models.DateField(default=None, verbose_name='Последнее обновление', null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Все оценки ЭК по заявке'
        verbose_name = 'Все оценки ЭК по заявке'

    def get_absolute_url(self):
        return reverse('score_expert_all_detail', args=[str(self.id)])

    @property
    def get_all_comments_and_scores(self):
        rel_exp_app = RelationExpertApplication.objects.all().filter(application=self.application).filter(
            common_commission=False).filter(is_active=True)
        scores_common = ScoreExpert.objects.all().filter(relation_exp_app__in=rel_exp_app)
        dict_all = {}
        for sc in scores_common:
            dict_all[sc.relation_exp_app.expert] = {}
            dict_all[sc.relation_exp_app.expert]['comment'] = sc.comment
            dict_all[sc.relation_exp_app.expert]['score1'] = sc.score1
            dict_all[sc.relation_exp_app.expert]['score2'] = sc.score2
            dict_all[sc.relation_exp_app.expert]['score3'] = sc.score3
            dict_all[sc.relation_exp_app.expert]['score4'] = sc.score4
            dict_all[sc.relation_exp_app.expert]['score5'] = sc.score5
            dict_all[sc.relation_exp_app.expert]['score'] = sc.score
        return dict_all

    def save(self, *args, **kwargs):
        self.full_clean()
        rel_exp_app = RelationExpertApplication.objects.all().filter(application=self.application).filter(
            common_commission=False).filter(is_active=True)
        scores_common = ScoreExpert.objects.all().filter(relation_exp_app__in=rel_exp_app)
        comments = []
        scores1 = []
        scores2 = []
        scores3 = []
        scores4 = []
        scores5 = []
        scores = []

        for sc in scores_common:
            comments.append(sc.comment)
            scores1.append(sc.score1)
            scores2.append(sc.score2)
            scores3.append(sc.score3)
            scores4.append(sc.score4)
            scores5.append(sc.score5)
            scores.append(sc.score)

        try:
            print(scores1, scores2, scores3, scores4, scores5, scores)
            self.score1 = mean_any(scores1)
            self.score2 = mean_any(scores2)
            self.score3 = mean_any(scores3)
            self.score4 = mean_any(scores4)
            self.score5 = mean_any(scores5)
            self.score = mean_any(scores)
        except MyError:
            print('not found socres')
        if not (self.score is None or self.comment_master is None or len(self.comment_master) == 0):
            self.check = True
        else:
            self.check = False
        self.date_last = datetime.now(tz=None)
        super(ScoreExpertAll, self).save(*args, **kwargs)


class ScoreAll(models.Model):
    """
    Все оценки
    """
    application = models.ForeignKey(Application, verbose_name='Заявка',
                                    on_delete=models.CASCADE, default=None, )
    score_com = models.FloatField(default=None, verbose_name='Оценка общей комиссии',
                                  blank=True, null=True)
    score_exp = models.FloatField(default=None, verbose_name='Оценка экспертной комиссии',
                                  blank=True, null=True)
    score_final = models.FloatField(default=None, verbose_name='Итоговая оценка',
                                    blank=True, null=True)
    date_last = models.DateField(default=None, verbose_name='Последнее обновление', null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Все оценки'
        verbose_name = 'Все оценки'

    def save(self, *args, **kwargs):
        self.full_clean()
        scores_common = ScoreCommonAll.objects.all().get(application=self.application).score
        print(scores_common)
        scores_expert = ScoreExpertAll.objects.all().get(application=self.application).score
        try:
            self.score_com = scores_common
            self.score_exp = scores_expert
            self.score_final = scalar_product_com_exp(com=scores_common, exp=scores_expert)
        except MyError:
            print('not found socres')
        if not (self.score_final is None):
            self.check = True
        else:
            self.check = False
        self.date_last = datetime.now(tz=None)
        super(ScoreAll, self).save(*args, **kwargs)



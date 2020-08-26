from result.models import CheckExpertScore
from django.core.exceptions import ObjectDoesNotExist
from score.models import ScoreExpert, ScoreCommon
from app.models import RelationExpertApplication

def checkscore_everywhere(request):
	count_all = 0
	count_ok = 0
	ready_score = False
	check_almost = False
	list_temp = []
	try:
		#получаем все заявки эксперта
		tmp = RelationExpertApplication.objects.all().filter(expert=request.user)
		#получаем его готовность
		check_almost = CheckExpertScore.objects.all().get(expert=request.user).check_exp
		#собираем все оценки эксперта по всем заявкам
		if request.user.common_commission:
			list_score_temp = [ temp for temp in ScoreCommon.objects.all() if temp.relation_exp_app.expert == request.user ]
		elif not request.user.common_commission:
			list_score_temp = [ temp for temp in ScoreExpert.objects.all() if temp.relation_exp_app.expert == request.user ]
		
		#считаем сколько всего заявок и сколько оценили полностью
		count_all = len(list_score_temp)
		for score in list_score_temp:
			if score.check:
				count_ok += 1
		if count_all - count_ok == 0:
			ready_score = True #все заявки оценили
		#здесь выводим "глобальный" словарь, эти переменные можно использовать на любом шаблоне
		return {'check_ready' : check_almost, 'ready_score' : ready_score, 'count_not' : count_all - count_ok, 'score_all' : count_all }
	except (NameError,AttributeError):
		return {'' : ''}
	except ObjectDoesNotExist:
		return {'check_ready' : check_almost, 'ready_score' : ready_score, 'count_not' : count_all - count_ok, 'score_all' : count_all }
	except:
		return {'' : ''}

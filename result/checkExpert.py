from result.models import CheckExpertScore
from django.core.exceptions import ObjectDoesNotExist
from score.models import ScoreExpert, ScoreCommon


def checkscore_com(request):
	count_all = 0
	count_ok = 0
	ready_score = False
	list_temp = []
	try:
		if request.user.common_commission:
			list_temp = ScoreCommon.objects.all()
		elif not request.user.common_commission:
			list_temp = ScoreExpert.objects.all()

		for score in list_temp:
			count_all += 1
			if score.check:
				count_ok += 1
		if count_all - count_ok == 0:
			ready_score = True

		return {'ready_score' : ready_score, 'count_not' : count_all - count_ok, 'score_all' : count_all }
	except NameError:
		return {'' : ''}
	except AttributeError:
		return {'' : ''}
	except ObjectDoesNotExist:
		return {'ready_score' : ready_score, 'count_not' : count_all - count_ok, 'score_all' : count_all }
		



def checkexpertscore_almost(request):
	check_ready = True
	if request.user.is_authenticated:
		try:
			check = CheckExpertScore.objects.all().get(expert=request.user)
			check_still = check.count_all - check.count_ok
			return { 'check_still': check_still, 'check_ready' : check.check_exp, 'check_all' : check.count_all }
		except NameError:
			return {'' : ''}
		except ObjectDoesNotExist:
			return {'' : ''}
	return {'' : ''}
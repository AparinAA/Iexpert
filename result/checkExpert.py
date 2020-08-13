from result.models import CheckExpertScore
from django.core.exceptions import ObjectDoesNotExist

def checkexpertscore_almost(request):
	check_ready = True
	if request.user.is_authenticated:
		try:
			check = CheckExpertScore.objects.all().get(expert=request.user)
			check_still = check.count_all - check.count_ok
			print(check.check_exp,check.count_all, check.count_ok, check_still)
			return { 'check_still': check_still, 'check_ready' : check.check_exp, 'check_all' : check.count_all }
		except NameError:
			return {'' : ''}
		except ObjectDoesNotExist:
			return {'' : ''}
	return {'' : ''}
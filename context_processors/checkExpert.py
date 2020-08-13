from result.models import CheckExpertScore

def checkexpertscore_almost(request):
	#print(CheckExpertScore.objects.all().get(expert=request.user))
	return {'check_still' : '1'}
	#check_still = CheckExpertScore.objects.all().get(expert=request.user).count_all - CheckExpertScore.objects.all().get(expert=request.user).count_ok
	#return {'check_still': check_still}
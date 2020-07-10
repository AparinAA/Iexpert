
def reload_scores(model):
    for mod in model.objects.all():
        mod.save()

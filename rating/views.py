from django.shortcuts import Http404, HttpResponseRedirect
from django.http import JsonResponse
from . import models
from django.core.exceptions import ObjectDoesNotExist


def like_view(request, pk, like):

    if like == 'like':
        like = True
    else:
        like = False

    try:
        rating_model = models.RatingModel.objects.get(pk=pk)
    except ObjectDoesNotExist:
        raise Http404

    try:
        vote = models.Vote.objects.get(target=rating_model,
                                       like=like,
                                       user=request.user)
        vote.delete()
    except ObjectDoesNotExist:
        try:
            vote = models.Vote.objects.get(target=rating_model,
                                           user=request.user)
            vote.change_like()
        except ObjectDoesNotExist:
            vote = models.Vote.objects.create(target=rating_model,
                                              like=like,
                                              user=request.user
                                              )
            vote.save()
    rating_model.calculate_score()

    if request.is_ajax():
        return JsonResponse({'likes': str(rating_model.likes),
                             'dislikes': str(rating_model.dislikes)})
    else:
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

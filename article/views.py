from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.http import JsonResponse, Http404
from django.db.models import Q
from django.views import generic
from comment.models import CommentModel
from tag.models import Tag
from .models import Article, Subscription
from .forms import ArticleForm
from comment.forms import CommentForm
from hitcount.views import HitCountMixIn
from django.core.exceptions import ObjectDoesNotExist


class AjaxResponseMixIn(object):
    def form_invalid(self, form):
        response = super().form_invalid(form)
        if self.request.is_ajax():
            data = {'error': form.errors}
            return JsonResponse(data)
        return response


class MainPage(generic.ListView):
    template_name = 'article/article_list.html'
    search_list = Article.objects.all().order_by('-created')
    tag = None
    paginate_by = 5

    def get_queryset(self):
        if self.tag:
            return Tag.get_articles_by_tag(self.tag)
        return self.search_list

    def dispatch(self, request, *args, **kwargs):
        if 'q' in request.GET:
            self.search_list = Article.objects.filter(Q(title__contains=request.GET['q']) |
                                                      Q(text__contains=request.GET['q'])
                                                      )
        if 'tag' in kwargs:
            self.tag = kwargs['tag']
        return super().dispatch(request, *args, **kwargs)


class SiteInfo(generic.TemplateView):
    template_name = 'main_page/info.html'


class Contacts(generic.TemplateView):
    template_name = 'main_page/contacts.html'


class CreateArticle(AjaxResponseMixIn, generic.FormView):
    form_class = ArticleForm
    template_name = 'article/add_article.html'
    article = None

    def get_success_url(self):
        return reverse('article-details', args=[self.article.primary_key])

    def form_valid(self, form):
        self.article = Article.objects.create(user=self.request.user,
                                              title=form.cleaned_data.get('title'),
                                              text=form.cleaned_data.get('text'))
        self.article.save()
        try:
            tag = Tag.objects.get(tag=form.cleaned_data.get('tag'))
            tag.article.add(self.article)
        except ObjectDoesNotExist:
            new_tag = Tag.objects.create(tag=form.cleaned_data.get('tag'),
                                         user=self.request.user)
            new_tag.save()
            new_tag.article.add(self.article)
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        if request.user is None:
            raise Http404
        return super().dispatch(request, *args, **kwargs)


class UpdateArticle(AjaxResponseMixIn, generic.FormView):
    form_class = ArticleForm
    template_name = 'article/add_article.html'
    article = None
    tag = None

    def get_success_url(self):
        return reverse('article-details', args=[self.article.primary_key])

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['article'] = self.article
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        initial['title'] = self.article.title
        initial['text'] = self.article.text
        initial['tag'] = self.tag
        return initial

    def form_valid(self, form):
        self.article.text = form.cleaned_data.get('text')
        self.article.title = form.cleaned_data.get('title')
        self.article.save()
        if self.tag is None:
            self.tag = Tag.objects.create(tag=form.cleaned_data.get('tag'),
                                          user=self.request.user)
            self.tag.article.add(self.article)
        else:
            self.tag.tag = form.cleaned_data.get('tag')
        self.tag.save()

        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        self.article = Article.objects.get(primary_key=kwargs['article_pk'])
        try:
            self.tag = Tag.objects.get(article=self.article)
        except ObjectDoesNotExist:
            self.tag = None
        return super().dispatch(request, *args, **kwargs)


class ArticleDetails(AjaxResponseMixIn, HitCountMixIn, generic.FormView):
    form_class = CommentForm
    article = None
    subscription = None
    template_name = 'article/article_details.html'

    def get_success_url(self):
        return reverse('article-details', args=[str(self.article.primary_key)])

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super(ArticleDetails, self).get_context_data(**kwargs)
        ctx['article'] = self.article
        ctx['comments'] = self.article.get_comment_list()
        return ctx

    def dispatch(self, request, *args, **kwargs):
        self.article = get_object_or_404(Article, pk=kwargs['article_pk'])
        self.add_hit(request, self.article.get_hit_counter())
        try:
            self.subscription = Subscription.objects.get(subscribed_user=self.request.user,
                                                         article=self.article)
            self.subscription.subscription_opened()
        except ObjectDoesNotExist:
            pass
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        if self.request.user.is_anonymous():
            raise Http404

        new_comment = form.save(commit=False)
        new_comment.text = self.request.POST['text']
        new_comment.user = self.request.user
        parent_pk = form['parent'].value()
        if parent_pk is not '' and parent_pk is not None:
            new_comment.parent = CommentModel.objects.get(pk=parent_pk)
        new_comment.article = self.article
        new_comment.save()
        response = super().form_valid(form)
        if self.request.is_ajax():
            data = {'text': new_comment.text,
                    'user': new_comment.user.username,
                    'created': new_comment.created,
                    'pk': self.article.primary_key,
                    }
            if parent_pk:
                data.update({'parent_pk': parent_pk})
            if self.subscription:
                self.subscription.subscription_opened()
            return JsonResponse(data)
        return response


class SubscriptionManagement(generic.RedirectView):
    article = None
    user = None
    subscription = None

    def get_redirect_url(self, *args, **kwargs):
        return reverse('article-details', args=[self.article.primary_key])

    def dispatch(self, request, *args, **kwargs):
        self.article = get_object_or_404(Article, primary_key=kwargs['primary_key'])
        self.user = self.request.user
        if self.user is None:
            return self.get_redirect_url(*args, **kwargs)

        try:
            self.subscription = Subscription.objects.get(article=self.article,
                                                         subscribed_user=self.user
                                                         )
            self.subscription.delete()
            data = {'message': 'Подписаться'}

        except ObjectDoesNotExist:
            self.subscription = Subscription.objects.create(article=self.article,
                                                            subscribed_user=self.user
                                                            )
            self.subscription.save()
            data = {'message': 'Отписаться'}

        if self.request.is_ajax():
            return JsonResponse(data)

        return super().dispatch(request, *args, **kwargs)


def delete_comment(request, pk):
    comment = CommentModel.objects.get(pk=pk)
    url = reverse('article-details', args=[comment.article.primary_key])
    comment.delete()
    if request.is_ajax():
        return JsonResponse({'text': 'сообщение успешно удалено'})
    else:
        return url

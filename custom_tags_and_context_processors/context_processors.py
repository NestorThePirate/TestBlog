from article.forms import SearchForm
from article.models import Article
from django.db.models import Count
from comment.models import CommentModel
from tag.models import Tag
from user.forms import LoginForm
from registration.forms import RegistrationForm


def search_form(request):
    form = SearchForm
    return {"SEARCH_FORM": form}


def recent_comments(request):
    comments = CommentModel.objects.order_by('-created')[:5]
    return {"RECENT_COMMENTS": comments}


def popular_articles(request):
    articles = Article.objects.get_popular_articles()[:5]
    return {'POPULAR_ARTICLES': articles}


def tags(request):
    tag_list = Tag.objects.all()
    return {"TAG_LIST": tag_list}

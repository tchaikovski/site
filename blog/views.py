from django.shortcuts import render, get_object_or_404
from .models import Post, Comment
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.views.generic import ListView
from .forms import EmailPostForm, CommentForm
from django.core.mail import send_mail
from taggit.models import Tag
from django.db.models import Count


class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'


def post_share(request, post_id):
    #  получение статьи по индификатору
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False
    if request.method == 'POST':
        #  Форма отправлена на сохранение
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # все поля прошли валидацию
            cd = form.cleaned_data
            # Отправка электронной почты
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = '{} ({}) recommends you reading "{}"' .format(cd['name'], cd['email'], post.title)
            message = 'Read "{}" at {}\n\n{}\'s comments: {}' .format(post.title, post_url, cd['name'], cd['comments'])
            send_mail(subject, message, 'test@adressayta.ru', [cd['to']])
            sent = True
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post': post, 'form': form, 'sent': sent})


def post_list(request, tag_slug=None):
    object_list = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])
    paginator = Paginator(object_list, 3)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    #  Если страница не является целым числом, возвращаем 1 страницу.

    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    #  Если число больше то возвращаем последнюю страницу

    return render(request, 'blog/post/list.html', {'page': page, 'posts': posts, 'tag': tag})


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post, status='published', publish__year=year, publish__month=month,
                             publish__day=day)
    #  Список активных коментов для статьи
    comments = post.comments.filter(active=True)
    new_comment = None
    # Формирвание списка похожих статей
    pos_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=pos_tags_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]
    if request.method == 'POST':
        #  пользователь отправил коммент
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # Создаем комент но не записываем
            new_comment = comment_form.save(commit=False)
            # Привязываем комент к статье
            new_comment.post = post
            # Сохраняем комент
            new_comment.save()
            comment_form.save_m2m()
    else:
        comment_form = CommentForm()
    return render(request, 'blog/post/detail.html', {'post': post, 'comments': comments, 'new_comment': new_comment,
                                                     'comment_form': comment_form, 'similar_posts': similar_posts})

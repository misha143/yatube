from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Count
from .models import Post, Group, Comment, Follow
from .forms import PostForm, CommentForm
from django.http import HttpResponseRedirect

from django.views.decorators.cache import cache_page

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required

User = get_user_model()


def page_not_found(request, exception):
    # Переменная exception содержит отладочную информацию,
    # выводить её в шаблон пользователской страницы 404 мы не станем
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)


# @cache_page(60 * 20)
def index(request):
    post_list = Post.objects.order_by('-pub_date').all()
    paginator = Paginator(post_list, 10)  # показывать по 10 записей на странице.

    page_number = request.GET.get('page')  # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number)  # получить записи с нужным смещением

    all_users = User.objects.all()
    users_list = []
    for u in all_users:
        users_list.append(u.username)
    users_list.sort()

    return render(
        request,
        'index.html',
        {'page': page, 'paginator': paginator, 'users_list': users_list}
    )


def profile(request, username):
    # тут тело функции
    user = get_object_or_404(User, username=username)
    posts_list = Post.objects.filter(author=user).order_by("-pub_date").all()
    posts_count = posts_list.count()
    paginator = Paginator(posts_list, 10)  # показывать по 10 записей на странице.
    page_number = request.GET.get('page')  # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number)  # получить записи с нужным смещением
    following = get_object_or_404(User, username=username)
    follower = get_object_or_404(User, username=request.user.username)
    is_follow = Follow.objects.filter(user=follower, author=following).count()
    cnt_of_following = Follow.objects.filter(user=following).count()
    cnt_of_followers = Follow.objects.filter(author=following).count()
    return render(request, 'profile.html',
                  {"profile": user, "posts_list": page, "paginator": paginator, "cnt_posts": posts_count,
                   "is_follow": is_follow, "cnt_of_following": cnt_of_following, "cnt_of_followers": cnt_of_followers})


def post_view(request, username, post_id):
    user = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=post_id)
    post_list = Post.objects.filter(author=user).all()
    form = CommentForm()
    comment_list = Comment.objects.filter(post=post).order_by("-created").all()
    posts_count = post_list.count()

    following = get_object_or_404(User, username=username)
    follower = get_object_or_404(User, username=request.user.username)
    is_follow = Follow.objects.filter(user=follower, author=following).count()
    cnt_of_following = Follow.objects.filter(user=following).count()
    cnt_of_followers = Follow.objects.filter(author=following).count()
    return render(request, 'post.html',
                  {"profile": user, "post": post, "cnt_posts": posts_count, "form": form, "comment_list": comment_list,
                   "is_follow": is_follow, "cnt_of_following": cnt_of_following, "cnt_of_followers": cnt_of_followers})


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, id=post_id)
    user = get_object_or_404(User, username=username)
    if request.user != user:
        return redirect("post", username=user.username, post_id=post_id)

    title = "Редактировать запись"
    btn_caption = "Сохранить"
    form = PostForm(request.POST or None, files=request.FILES or None, instance=post)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("post", username=request.user.username, post_id=post_id)
    return render(request, "post_edit.html", {"form": form, "title": title, "btn_caption": btn_caption, "post": post})


@login_required
def post_delete(request, username, post_id):
    if request.user.username != username:
        return redirect(f"/{username}/{post_id}")
    post = get_object_or_404(Post, pk=post_id)
    post.delete()
    return redirect("profile", username=username)


# view-функция для страницы сообщества
def group_posts(request, slug):
    # функция get_object_or_404 получает по заданным критериям объект из базы данных
    # или возвращает сообщение об ошибке, если объект не найден
    group = get_object_or_404(Group, slug=slug)

    # Метод .filter позволяет ограничить поиск по критериям. Это аналог добавления
    # условия WHERE group_id = {group_id}
    # posts = Post.objects.filter(group=group)[:12]
    post_list = Post.objects.filter(group=group).all()
    paginator = Paginator(post_list, 10)  # показывать по 10 записей на странице.

    page_number = request.GET.get('page')  # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number)  # получить записи с нужным смещением

    return render(request, "group.html", {"group": group, 'page': page, 'paginator': paginator})


@login_required
def new_post(request):
    title = "Добавить запись"
    btn_caption = "Добавить"
    form = PostForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect("index")
    form = PostForm()
    context = {
        "form": form,
        "title": title,
        "btn_caption": btn_caption
    }
    return render(request, "post_edit.html", context)


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.author = request.user
            new_comment.post = post
            new_comment.save()
            return redirect("post", username=post.author.username, post_id=post_id)
    form = PostForm()


@login_required
def comment_delete(request, username, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.user.username == comment.author.username:
        comment.delete()
    return redirect("post", username=username, post_id=post_id)


@login_required
def follow_index(request):
    following = Follow.objects.filter(user=request.user).all()
    author_list = []
    following_list = []
    for author in following:
        author_list.append(author.author.id)
        following_list.append(author.author.username)

    post_list = Post.objects.filter(author__in=author_list).order_by("-pub_date").all()

    paginator = Paginator(post_list, 10)  # показывать по 10 записей на странице.
    page_number = request.GET.get('page')  # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number)  # получить записи с нужным смещением
    return render(
        request,
        'follow.html',
        {'page': page, 'paginator': paginator, 'following_list': following_list}
    )


@login_required
def profile_follow(request, username):
    following = get_object_or_404(User, username=username)
    follower = get_object_or_404(User, username=request.user.username)
    try:
        # уникальные в связке
        Follow.objects.create(user=follower, author=following)
    except:
        # в случае если уже была создана связь между двумя людьми
        pass
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def profile_unfollow(request, username):
    following = get_object_or_404(User, username=username)
    follower = get_object_or_404(User, username=request.user.username)
    try:
        # уникальные в связке
        Follow.objects.filter(user=follower, author=following).delete()
    except:
        # в случае если уже была создана связь между двумя людьми
        pass
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

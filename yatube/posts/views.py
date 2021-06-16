from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Count
from .models import Post, Group
from .forms import PostForm

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required

User = get_user_model()


def index(request):
    post_list = Post.objects.order_by('-pub_date').all()
    paginator = Paginator(post_list, 10)  # показывать по 10 записей на странице.

    page_number = request.GET.get('page')  # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number)  # получить записи с нужным смещением
    return render(
        request,
        'index.html',
        {'page': page, 'paginator': paginator}
    )


def profile(request, username):
    # тут тело функции
    user = get_object_or_404(User, username=username)
    posts_list = Post.objects.filter(author=user).order_by("-pub_date").all()
    posts_count = posts_list.count()
    paginator = Paginator(posts_list, 10)  # показывать по 10 записей на странице.
    page_number = request.GET.get('page')  # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number)  # получить записи с нужным смещением
    return render(request, 'profile.html',
                  {"profile": user, "posts_list": page, "paginator": paginator, "cnt_posts": posts_count})


def post_view(request, username, post_id):
    user = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=post_id)
    post_list = Post.objects.filter(author=user).all()
    posts_count = post_list.count()
    return render(request, 'post.html', {"profile": user, "post": post, "cnt_posts": posts_count})


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

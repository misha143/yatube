from django.shortcuts import render, get_object_or_404, redirect

from .models import Post, Group
from .forms import PostForm

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required

User = get_user_model()


def index(request):
    latest = Post.objects.order_by("-pub_date")[:11]
    return render(request, "index.html", {"posts": latest})


# view-функция для страницы сообщества
def group_posts(request, slug):
    # функция get_object_or_404 получает по заданным критериям объект из базы данных
    # или возвращает сообщение об ошибке, если объект не найден
    group = get_object_or_404(Group, slug=slug)

    # Метод .filter позволяет ограничить поиск по критериям. Это аналог добавления
    # условия WHERE group_id = {group_id}
    posts = Post.objects.filter(group=group)[:12]
    return render(request, "group.html", {"group": group, "posts": posts})


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

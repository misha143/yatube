from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # импорт правил из приложения posts
    path("", include("posts.urls")),

    #  регистрация и авторизация
    path("auth/", include("users.urls")),

    #  если нужного шаблона для /auth не нашлось в файле users.urls —
    #  ищем совпадения в файле django.contrib.auth.urls
    path("auth/", include("django.contrib.auth.urls")),

    # импорт правил из приложения admin
    path("admin/", admin.site.urls),
]

from django.contrib import admin

from .models import Post, Group


class PostAdmin(admin.ModelAdmin):
    # перечисляем поля, которые должны отображаться в админке
    list_display = ("text", "pub_date", "author", "group")
    # добавляем интерфейс для поиска по тексту постов
    search_fields = ("text",)
    # добавляем возможность фильтрации по дате
    list_filter = ("pub_date",)
    empty_value_display = "-пусто-"

class GroupAdmin(admin.ModelAdmin):
    # перечисляем поля, которые должны отображаться в админке
    list_display = ("title", "slug", "description")
    # добавляем интерфейс для поиска по тексту постов
    search_fields = ("title",)
    empty_value_display = "-пусто-"


admin.site.register(Post, PostAdmin)

admin.site.register(Group, GroupAdmin)

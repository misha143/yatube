from django.contrib import admin

from .models import Post, Group


class PostAdmin(admin.ModelAdmin):
    # перечисляем поля, которые должны отображаться в админке
    list_display = ("text", "pub_date", "author")
    # добавляем интерфейс для поиска по тексту постов
    search_fields = ("text",)
    # добавляем возможность фильтрации по дате
    list_filter = ("pub_date",)

class GroupAdmin(admin.ModelAdmin):
    # перечисляем поля, которые должны отображаться в админке
    list_display = ("title", "slug", "description")
    # добавляем интерфейс для поиска по тексту постов
    search_fields = ("title",)


admin.site.register(Post, PostAdmin)

admin.site.register(Group, GroupAdmin)

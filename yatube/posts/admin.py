from django.contrib import admin

from .models import Comment, Group, Post


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 1
    show_change_link = True


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('pk', 'text', 'pub_date', 'author', 'group')
    list_editable = ('group',)
    list_filter = ('pub_date', 'group')
    search_fields = ('text',)
    empty_value_display = '-пусто-'
    inlines = [CommentInline]


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'description')
    list_editable = ('slug',)
    empty_value_display = '-пусто-'
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('text', 'post', 'author', 'created')
    list_filter = ('created', 'author')
    search_fields = ('text',)
    empty_value_display = '-пусто-'

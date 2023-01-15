from django.contrib import admin

from .models import Group, Post


class PostAdmin(admin.ModelAdmin):
    list_display = ('pk', 'text', 'pub_date', 'author', 'group')
    list_editable = ('group',)
    list_filter = ('pub_date', 'group')
    search_fields = ('text',)
    empty_value_display = '-пусто-'


admin.site.register(Post, PostAdmin)
admin.site.register(Group)

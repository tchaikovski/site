from django.contrib import admin
from .models import Post, Comment, TaggedPost, TaggableManager, TaggedItemBase


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'author', 'publish', 'status')
    list_filter = ('status', 'created', 'publish', 'author')
    search_fields = ('title', 'body')
    preserve_filters = {'slug': ('title', )}
    raw_id_fields = ('author', )
    date_hierarchy = 'publish' # поиск по датам
    ordering = ('status', 'publish')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'post', 'created', 'active')
    list_filter = ('active', 'created', 'updated')
    search_fields = ('name', 'email', 'body')

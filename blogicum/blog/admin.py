from django.contrib import admin
from django.contrib.auth.models import Group

from .models import Location, Category, Post

admin.site.empty_value_display = 'не задано'


class PostInline(admin.TabularInline):
    model = Post
    extra = 0


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    inlines = (PostInline,)
    list_display = ('title',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'text',
        'created_at',
        'is_published',
        'pub_date',
        'author',
        'location',
        'category',
    )
    list_editable = (
        'is_published',
        'category',
    )
    search_fields = ('title',)
    list_filter = ('category',)
    list_display_links = ('title',)


admin.site.register(Location)
admin.site.unregister(Group)

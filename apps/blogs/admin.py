from django.contrib import admin
from .models import Blog, Category, Tag
# Ghi chú: Để slug tiếng Việt không bị lỗi dấu, hãy nhập slug không dấu hoặc dùng script import đã sửa.

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'publish_time')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'category', 'intro')
    list_filter = ('category',)
    filter_horizontal = ('tags',)  # Vì tags là ManyToManyField
    list_per_page = 20

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    list_per_page = 20

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}  # Nếu nhập tiếng Việt, nên sửa lại slug không dấu 
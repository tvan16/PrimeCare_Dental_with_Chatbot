from django.views.generic import ListView, DetailView
from .models import Blog
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
import json
import os
from datetime import datetime
from django.utils import timezone


class BlogListView(ListView):
    model = Blog
    template_name = 'blogs/list.html'
    context_object_name = 'blogs'
    paginate_by = 10
    ordering = ['-publish_time']

class BlogDetailView(DetailView):
    model = Blog
    template_name = 'blogs/detail.html'
    context_object_name = 'blog'
    slug_field = 'slug'
    slug_url_kwarg = 'slug' 

# Các trang tĩnh (nếu cần, dùng chung template với services/pages)
def about(request):
    return render(request, 'pages/about-VN.html')

def contact(request):
    return render(request, 'pages/contact.html')

def faqs(request):
    return render(request, 'pages/faqs.html')

def testimonials(request):
    return render(request, 'pages/testimonials.html')

def gallery(request):
    return render(request, 'pages/gallery.html')

def terms(request):
    return render(request, 'pages/terms.html')

def privacy(request):
    return render(request, 'pages/privacy.html')

def support(request):
    return render(request, 'pages/support.html')

def price_list(request):
    return render(request, 'pages/price-list.html')

def blog_list(request):
    posts = Blog.objects.all().order_by('-publish_time')
    paginator = Paginator(posts, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    is_paginated = page_obj.has_other_pages()
    context = {
        'page_obj': page_obj,
        'is_paginated': is_paginated,
    }
    return render(request, 'blogs/list.html', context)

def blog_detail(request, slug):
    try:
        blog = Blog.objects.get(slug=slug)
        # Lấy 3 bài viết khác bất kỳ (trừ bài hiện tại)
        related_blogs = Blog.objects.exclude(id=blog.id).order_by('?')[:3]
        return render(request, 'blogs/detail.html', {'blog': blog, 'related_blogs': related_blogs})
    except Blog.DoesNotExist:
        # Nếu không có, tìm trong JSON
        json_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'news-data.json')
        with open(json_file_path, 'r', encoding='utf-8') as file:
            posts = json.load(file)
        post = next((p for p in posts if p['slug'] == slug), None)
        if post is None:
            return render(request, '404.html')
        return render(request, 'blogs/detail.html', {'blog': post})
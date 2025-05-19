from django.db import models
from django.utils import timezone
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True)

    def __str__(self):
        return self.name

class Blog(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    category = models.CharField(max_length=255)
    tags = models.ManyToManyField('Tag', blank=True)
    image = models.ImageField(upload_to='blog_images/', blank=True, null=True)
    intro = models.TextField()
    detail_content_1 = models.TextField(blank=True)
    detail_content_2 = models.TextField(blank=True)
    quote = models.TextField(blank=True)
    detail_content_3 = models.TextField(blank=True)
    title = models.CharField(max_length=255, blank=True)
    detail_content_4 = models.TextField(blank=True)
    detail_content_5 = models.TextField(blank=True)
    publish_time = models.DateTimeField()

    def __str__(self):
        return self.name 
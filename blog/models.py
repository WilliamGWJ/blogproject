import markdown
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.html import strip_tags


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Post(models.Model):
    title = models.CharField(max_length=100)
    body = models.TextField()
    create_time = models.DateTimeField()
    modified_time = models.DateTimeField(auto_now_add=True)
    excerpt = models.CharField(max_length=200, blank=True)
    views = models.PositiveIntegerField(default=0)
    # 外键-文章分类-一对多
    category = models.ForeignKey(Category)
    # 外键-文章标签-多对多
    tag = models.ManyToManyField(Tag, blank=True)
    # 外键-文章作者-使用User类
    author = models.ForeignKey(User)

    # 统计文章的阅读量
    def increase_views(self):
        self.views += 1
        self.save(update_fields=['views'])

    # 如果摘要为空，则使用文章的前50个字符作为摘要
    def save(self, *args, **kwargs):
        if not self.excerpt:
            md = markdown.Markdown(
                extensions=[
                    'markdown.extensions.extra',
                    'markdown.extensions.codehilite',
                ])
            self.excerpt = strip_tags(md.convert(self.body))[:50]
        super(Post, self).save(*args, **kwargs)

    # 定义文章列表默认排列顺序，按时间倒序排列
    class Meta:
        ordering = ['-create_time']

    # 自定义get_absolute_url方法，返回post的url
    def get_absolute_url(self):
        return reverse('blog:detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.title

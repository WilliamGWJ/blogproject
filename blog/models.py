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

    # 如果摘要为空，则使用文章的前100个字符作为摘要
    def save(self, *args, **kwargs):
        # 如果没有填写摘要
        if not self.excerpt:
            # 首先实例化一个 Markdown 类，用于渲染 body 的文本
            md = markdown.Markdown(extensions=[
                'markdown.extensions.extra',
                'markdown.extensions.codehilite',
            ])
            # 先将 Markdown 文本渲染成 HTML 文本
            # strip_tags 去掉 HTML 文本的全部 HTML 标签
            # 从文本摘取前 100 个字符赋给 excerpt
            self.excerpt = strip_tags(md.convert(self.body))[:100]

        # 调用父类的 save 方法将数据保存到数据库中
        super(Post, self).save(*args, **kwargs)

    # 定义文章列表默认排列顺序，按时间倒序排列
    class Meta:
        ordering = ['-create_time']

    # 自定义get_absolute_url方法，返回post的url
    def get_absolute_url(self):
        return reverse('blog:detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.title

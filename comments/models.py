from django.db import models


class Comment(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    url = models.URLField(blank=True)
    text = models.TextField()
    create_time = models.DateTimeField(auto_now_add=True)
    # 外键-评论与文章-一对多
    post = models.ForeignKey('blog.Post')

    # 默认返回评论的前20字
    def __str__(self):
        return self.text[:20]
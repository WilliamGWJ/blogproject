import markdown
from markdown.extensions.toc import TocExtension
import functools
from django.shortcuts import render, get_object_or_404
from comments.forms import CommentForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView, DetailView
from django.utils.text import slugify
from .models import Post, Category, Tag


# 主页视图函数，加入分页功能
class IndexView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    # 打开分页选项
    paginate_by = 3

    # 复写get_context_data方法，加入自定义的模板变量
    def get_context_data(self, **kwargs):
        # 获得父类生成的传递给模板的字典
        context = super().get_context_data(**kwargs)

        # 从模板字典中取出对应变量
        paginator = context.get('paginator')
        page_obj = context.get('page_obj')
        is_paginated = context.get('is_paginated')

        # 调用自定义的pagination_data方法获得显示分页导航条需要的数据
        pagination_data = self.pagination_data(paginator, page_obj, is_paginated)

        # 将分页导航条的模板变量更新到context中
        context.update(pagination_data)

        # 将更新后的context返回，以便ListView使用这个字典中的模板变量去渲染模板
        return context

    # 自定义的方法，用于显示分页导航条需要的数据
    def pagination_data(self, paginator, page_obj, is_paginated):
        # 如果没有分页，则无需显示导航条
        if not is_paginated:
            return {}

        # 是否需要显示第 1 页的页码号
        first = False
        # 是否需要显示最后一页的页码号
        last = False
        # 当前页左边连续的页码号
        left = []
        # 当前页右边连续的页码号，初始值为空
        right = []
        # 标示第 1 页页码后是否需要显示省略号
        left_has_more = False
        # 标示最后一页页码前是否需要显示省略号
        right_has_more = False
        # 获得用户当前请求的页码数
        page_number = page_obj.number
        # 获得分页总页数
        total_pages = paginator.num_pages
        # 获得整个分页列表
        page_range = paginator.page_range

        # 如果当前页码数为1
        if page_number == 1:
            # 获取当前页码的右边两个页码
            right = page_range[page_number:page_number+2]
            # right[-1]页码比最后一页小，显示最后一页
            if right[-1] < total_pages:
                last = True
            # right[-1]页码比最后一页前一个页的页码号小，显示右边的省略号
            if right[-1] < total_pages - 1:
                right_has_more = True

        # 当前页码为最后一页
        elif page_number == total_pages:
            # 获取当前页码的左边两个页码
            left = page_range[(page_number-3) if (page_number - 3) > 0 else 0:(page_number - 1)]
            # left[0]页码比第一页大，显示第一页
            if left[0] > 1:
                first = True
            # left[0]页码比第二页大，显示省略号
            if left[0] > 2:
                left_has_more = True

        else:
            # 获取当前页码左右两边各两个页码
            left = page_range[(page_number - 3) if (page_number - 3) > 0 else 0:(page_number-1)]
            right = page_range[page_number:page_number+2]

            # 设置是否显示第一&最后一页，是否显示省略号
            if right[-1] < total_pages - 1:
                right_has_more = True
            if right[-1] < total_pages:
                last = True

            if left[0] > 2:
                left_has_more = True
            if left[0] > 1:
                first = True

        data = {
            'left': left,
            'right': right,
            'first': first,
            'last': last,
            'left_has_more': left_has_more,
            'right_has_more': right_has_more,
        }
        return data


# 分类页面(继承自主页面的通用视图函数)
class CategoryView(IndexView):
    # 复写get_queryset方法，该方法默认获取指定模型的全部列表数据
    def get_queryset(self):
        cate = get_object_or_404(Category, pk=self.kwargs.get('pk'))
        return super(CategoryView, self).get_queryset().filter(category=cate)


# 标签页面（继承继承自主页面的通用视图函数）
class TagView(IndexView):
    # 复写get_queryset方法，该方法默认获取指定模型的全部列表数据
    def get_queryset(self):
        tag = get_object_or_404(Tag, pk=self.kwargs.get('pk'))
        return super(TagView, self).get_queryset().filter(tag=tag)


# 分类页面（继承继承自主页面的通用视图函数）
class ArchiveView(IndexView):
    def get_queryset(self):
        year = self.kwargs.get('year')
        month = self.kwargs.get('month')
        return super(ArchiveView, self).get_queryset().filter(create_time__year=year,
                                                              create_time__month=month
                                                              )


# 文章详情页面（继承自DetailView）
class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'

    # 覆写get方法，目的是因为每当文章被访问一次，就得将文章阅读量+1
    def get(self, request, *args, **kwargs):
        response = super(PostDetailView, self).get(request, *args, **kwargs)

        # 文章阅读量+1
        self.object.increase_views()

        # 视图函数返回一个HttpResponse对象
        return response

    # 覆写 get_object 方法的目的是因为需要对 post 的 body 值进行渲染
    def get_object(self, queryset=None):
        post = super(PostDetailView, self).get_object(queryset=None)
        md = markdown.Markdown(extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.codehilite',
            TocExtension(slugify=slugify),
        ])
        post.body = md.convert(post.body)
        post.toc = md.toc
        return post

    # 覆写 get_context_data 的目的是因为除了将 post 传递给模板外还要把评论表单、post 下的评论列表传递给模板。
    def get_context_data(self, **kwargs):
        context = super(PostDetailView, self).get_context_data(**kwargs)
        form = CommentForm()
        comment_list = self.object.comment_set.all()
        context.update({
            'form': form,
            'comment_list': comment_list
        })
        return context


# 文章详情页视图函数（弃用）
def detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.increase_views()
    post.body = markdown.markdown(
        post.body,
        extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.codehilite',
            'markdown.extensions.toc',
        ])
    form = CommentForm()
    comment_list = post.comment_set.all()
    context = {
        'post': post,
        'form': form,
        'comment_list': comment_list
    }
    return render(request, 'blog/detail.html', context=context)


# 主页视图函数（弃用）
"""
# def index(request):
#     object_list = Post.objects.all()
#     paginator = Paginator(object_list, 5)
#
#     page = request.GET.get('page')
#     try:
#         page_obj = paginator.page(page)
#     except PageNotAnInteger:
#         page_obj = paginator.page(1)
#     except EmptyPage:
#         page_obj = paginator.page(paginator.num_pages)
#
#     post_list = page_obj.object_list
#
#     context = {'post_list': post_list, 'paginator': paginator, 'page_obj': page_obj}
#     %s
"""


# 分类页面视图函数(弃用)
"""
def category(request, pk):
    cate = get_object_or_404(Category, pk=pk)
    post_list = Post.objects.filter(category=cate)
    return render(request, 'blog/index.html', context={'post_list': post_list})
"""


# 标签视图函数（弃用）
"""
def tag(request, pk):
    tag = get_object_or_404(Tag, pk=pk)
    post_list = Post.objects.filter(tag=tag)
    return render(request, 'blog/index.html', context={'post_list': post_list})
"""


# 分类页面视图函数（弃用）
"""
def archives(request, year, month):

    post_list = Post.objects.filter(created_time__year=year, 
                                    created_time__month=month
                                    )

    return render(request, 'blog/index.html', context={'post_list': post_list})
"""


# 自定义分页装饰器（弃用）
"""
def auto_paginator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        is_paginated = True
        object_list = func.post_list
        paginator = Paginator(object_list, 3)
        page = func.request.GET.get('page')
        page_obj = paginator.page(page)
        post_list = page_obj.object_list
        context = {'post_list': post_list}
        pagination_data = IndexView.pagination_data(paginator, page_obj, is_paginated)
        context.update(pagination_data)
        func.context = context
        return func(*args, **kwargs)
    return wrapper
"""

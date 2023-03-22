from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.cache import cache_page
from .models import Post, Group, User
from .forms import PostForm, CommentForm


SHOWN_POSTS_NUMBER: int = 10
SHOWN_TITLE_CHAR_COUNT: int = 30


@cache_page(20, key_prefix='index_page')
def index(request):
    posts_list = Post.objects.select_related('group')
    paginator = Paginator(posts_list, SHOWN_POSTS_NUMBER)
    page_num = request.GET.get('page')
    page_obj = paginator.get_page(page_num)
    context = {
        'page_obj': page_obj
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts_list = group.posts.select_related('group')
    paginator = Paginator(posts_list, SHOWN_POSTS_NUMBER)
    page_num = request.GET.get('page')
    page_obj = paginator.get_page(page_num)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts_list = author.posts.select_related('group')
    paginator = Paginator(posts_list, SHOWN_POSTS_NUMBER)
    page_num = request.GET.get('page')
    page_obj = paginator.get_page(page_num)
    total_posts = paginator.count
    context = {
        'total_posts': total_posts,
        'page_obj': page_obj,
        'username': author,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    title = post.text[:SHOWN_TITLE_CHAR_COUNT]
    posts_count = post.author.posts.count()
    comments = post.comments.all()
    form = CommentForm(request.POST or None)
    context = {
        'form': form,
        'comments': comments,
        'posts_count': posts_count,
        'post': post,
        'title': title
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None,
                    files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', username=request.user)
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    is_edit: bool = True
    post_obj = get_object_or_404(Post, pk=post_id)
    if post_obj.author == request.user:
        form = PostForm(
            request.POST or None,
            files=request.FILES or None,
            instance=post_obj
        )
        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', post_id=post_id)
        return render(
            request, 'posts/create_post.html',
            {'form': form, 'is_edit': is_edit},
        )
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)

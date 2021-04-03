from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import PostForm, CommentForm
from .models import Group, Post, User, Follow
from yatube import settings


def index(request):
    latest = Post.objects.all()
    paginator = Paginator(latest, settings.PAR_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'index.html',
        {'page': page}
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, settings.PAR_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'group.html',
        {'group': group, 'page': page}
    )


@login_required
def post_new(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if not form.is_valid():
        return render(
            request, 'post_new.html', {'form': form, 'edit': False})
    new_post = form.save(commit=False)
    new_post.author = request.user
    new_post.save()
    return redirect('index')


def profile(request, username):
    user = get_object_or_404(User, username=username)
    user_posts = user.posts.all()
    post_count = user.posts.count()
    paginator = Paginator(user_posts, settings.PAR_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    following = request.user.is_authenticated and Follow.objects.filter(
        user=request.user, author=user).exists()
    follow_count = Follow.objects.filter(author=user).count()
    following_count = Follow.objects.filter(user=user).count()
    context = {
        'profile': user,
        'page': page,
        'post_count': post_count,
        'following': following,
        'follow_count': follow_count,
        'following_count': following_count, }
    return render(request, 'profile.html', context)


def post_view(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    post_count = post.author.posts.count()
    follow_count = post.author.follower.all().count()
    following_count = post.author.following.all().count()
    form = CommentForm()
    comments = post.comments.all()
    context = {'post': post,
               'profile': post.author,
               'post_count': post_count,
               'form': form,
               'comments': comments,
               'follow_count': follow_count,
               'following_count': following_count, }
    return render(request, 'post.html', context)


@login_required
def post_edit(request, username, post_id):
    current_user = request.user
    post = get_object_or_404(Post, id=post_id, author__username=username)
    if current_user != post.author:
        return redirect(reverse('post', kwargs={'username': username,
                                'post_id': post.id}))
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('post', username, post_id)
    context = {'form': form, 'edit': True, 'post': post}
    return render(request, 'post_new.html', context)


def page_not_found(request, exception):
    # Переменная exception содержит отладочную информацию,
    # выводить её в шаблон пользователской страницы 404 мы не станем
    return render(
        request,
        'misc/404.html',
        {'path': request.path},
        status=404
    )


def server_error(request):
    return render(request, 'misc/500.html', status=500)


@login_required
def add_comment(request, post_id, username):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect('post', username, post_id)
    context = {'form': form, 'post_id': post_id, 'username': username}
    return render(request, 'comments.html', context)


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'page': page, 'paginator': paginator,
    }
    return render(request, 'follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(user=request.user, author=author,)
    return redirect('profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.filter(user=request.user, author=author).delete()
    return redirect('profile', username=username)

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.db.models.query import QuerySet
from django.shortcuts import redirect, get_object_or_404, render
from django.utils import timezone
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView, DetailView, DeleteView, ListView, UpdateView
)
from django.db.models import Count

from .models import Comment, Post, User
from .forms import PostForm, CommentForm, ProfileForm
from .constants import PAGINATE_POST


class PostMixin:
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'


class CommentMixin:
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'


class IndexListView(ListView):
    """Главная страница"""

    model = Post
    template_name = 'blog/index.html'
    paginate_by = PAGINATE_POST

    def get_queryset(self):
        return Post.objects.select_related(
            'location', 'author', 'category'
        ).filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True,
        ).order_by('-pub_date').annotate(comment_count=Count('comment'))


class PostDetailView(LoginRequiredMixin, DetailView):
    """Страница отдельного поста"""

    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'


class CategoryListView(ListView):
    """Страница отделоной категории"""

    model = Post
    template_name = 'blog/category.html'


class ProfileListView(ListView):
    """Страница пользователя профиля"""

    model = Post
    template_name = 'blog/profile.html'
    paginate_by = PAGINATE_POST

    def get_queryset(self):
        return (
            self.model.objects.select_related('author')
            .filter(author__username=self.kwargs['username'])
            .annotate(comment_count=Count("comment"))
            .order_by("-pub_date"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(
            User,
            username=self.kwargs['username'])
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование профиля"""

    model = User
    form_class = ProfileForm
    template_name = 'blog/user.html'


class PostCreateView(LoginRequiredMixin, CreateView):
    """Создание нового поста"""

    model = Post
    template_name = 'blog/create.html'
    form_class = PostForm

    def get_success_url(self):
        username = self.request.user.username
        success_url = reverse_lazy(
            'blog:profile',
            kwargs={'username': username}
        )
        return success_url


class PostUpdateView(LoginRequiredMixin, PostMixin, UpdateView):
    """Редактирование поста"""

    form_class = PostForm


class PostDeleteView(LoginRequiredMixin, PostMixin, DeleteView):
    """Удаление поста"""


class CommentCreateView(LoginRequiredMixin, CreateView):
    """Написание коментария"""

    model = Comment
    form_class = CommentForm
    success_url = reverse_lazy('blog:post_detail')


class CommentUpdateView(LoginRequiredMixin, CommentMixin, UpdateView):
    """Редактирование коментария"""

    form_class = CommentForm


class CommentDeleteView(LoginRequiredMixin, CommentMixin, DeleteView):
    """Удаление коментария"""

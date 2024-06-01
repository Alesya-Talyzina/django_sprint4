from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.shortcuts import redirect, get_object_or_404
from django.utils import timezone
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView, DetailView, DeleteView, ListView, UpdateView
)
from django.db.models import Count

from .models import Comment, Post, User
from .forms import PostForm, CommentForm, ProfileForm
from .constants import PAGINATE_BY


class PostMixin:
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    ''' def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return redirect('blog:post_detail', self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs) '''


class CommentMixin:
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    ''' def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return redirect('blog:post_detail', self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs) '''


class IndexListView(ListView):
    """Главная страница"""

    model = Post
    template_name = 'blog/index.html'
    paginate_by = PAGINATE_BY


class PostDetailView(LoginRequiredMixin, DetailView):
    """Страница отдельного поста"""

    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    '''def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related('author')
        )
        return context

    def get_object(self):
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        if self.request.user == post.author:
            return post
        return get_object_or_404(
            Post, is_published=True, category__is_published=True,
            pub_date__lt=timezone.now(), pk=self.kwargs['post_id'])'''


class CategoryListView(ListView):
    """Страница отделоной категории"""

    model = Post
    template_name = 'blog/category.html'
    paginate_by = PAGINATE_BY

    ''' def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context '''


class ProfileListView(ListView):
    """Страница пользователя профиля"""

    model = Post
    template_name = 'blog/profile.html'
    paginate_by = PAGINATE_BY

    '''def get_object(self):
        return get_object_or_404(User, username=self.kwargs['username'])

    def get_context_data(self, **kwargs):
        return dict(
            **super().get_context_data(**kwargs),
            profile=self.get_object()
        )'''


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование профиля"""

    model = User
    form_class = ProfileForm
    template_name = 'blog/user.html'


class PostCreateView(LoginRequiredMixin, CreateView):
    """Создание нового поста"""

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:post_detail')

    ''' def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form) '''


class PostUpdateView(LoginRequiredMixin, PostMixin, UpdateView):
    """Редактирование поста"""

    form_class = PostForm


class PostDeleteView(LoginRequiredMixin, PostMixin, DeleteView):
    """Удаление поста"""

    ''' def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.object)
        return context '''


class CommentCreateView(LoginRequiredMixin, CreateView):
    """Написание коментария"""

    model = Comment
    form_class = CommentForm
    success_url = reverse_lazy('blog:post_detail')

    ''' def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form) '''


class CommentUpdateView(LoginRequiredMixin, CommentMixin, UpdateView):
    """Редактирование коментария"""

    form_class = CommentForm


class CommentDeleteView(LoginRequiredMixin, CommentMixin, DeleteView):
    """Удаление коментария"""

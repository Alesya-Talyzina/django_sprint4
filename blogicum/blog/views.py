from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)

from blog.constants import PAGE_PAGINATOR
from blog.forms import CommentForm, PostForm, ProfileForm
from blog.mixin import CommentMixin, PostMixin, PostQuerySetMixin
from blog.models import Category, Comment, Post, User


class IndexListView(PostQuerySetMixin, ListView):
    """Главная страница"""

    paginate_by = PAGE_PAGINATOR
    template_name = 'blog/index.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset


class PostDetailView(DetailView):
    """Страница отдельного поста"""

    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_object(self, queryset=None):
        object = super().get_object(
            self.model.objects.select_related(
                'location', 'category', 'author'
            ),
        )
        if object.author != self.request.user:
            return get_object_or_404(
                self.model.objects.select_related(
                    'location', 'category', 'author'
                ).filter(
                    pub_date__lte=timezone.now(),
                    category__is_published=True,
                    is_published=True
                ),
                pk=self.kwargs['post_id']
            )
        return object

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related(
                'author'
            ).order_by('created_at')
        )
        return context


class CategoryListView(PostQuerySetMixin, ListView):
    """Страница отдельной категории."""

    template_name = 'blog/category.html'
    category = None
    paginate_by = PAGE_PAGINATOR

    def get_queryset(self):
        self.category = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )
        return super().get_queryset().filter(
            category=self.category
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class ProfileListView(PostQuerySetMixin, ListView):
    """Страница профиля пользователя"""

    model = Post
    template_name = 'blog/profile.html'
    paginate_by = PAGE_PAGINATOR

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = User.objects.get(username=self.kwargs['username'])
        return context

    def get_queryset(self):
        self.author = get_object_or_404(User, username=self.kwargs['username'])
        if self.author.username == self.kwargs['username']:
            return self.annotate_comment_count(
                Post.objects.select_related(
                    'location', 'category', 'author'
                ).filter(
                    author=self.author
                ).order_by('-pub_date'))

        return super().get_queryset().filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True,
        )


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """редактирование страницы профиля пользователя"""

    model = User
    form_class = ProfileForm
    template_name = 'blog/user.html'

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username},
        )


class PostCreateView(LoginRequiredMixin, CreateView):
    """Страница написания поста"""

    model = Post
    template_name = 'blog/create.html'
    form_class = PostForm

    def get_success_url(self):
        username = self.request.user.username
        success_url = reverse(
            'blog:profile',
            kwargs={'username': username}
        )
        return success_url

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, PostMixin, UpdateView):
    """Редактирование поста"""

    def test_func(self):
        return self.get_object().author == self.request.user

    def handle_no_permission(self):
        post = self.get_object()
        return redirect('blog:post_detail', post.pk)

    def get_object(self, queryset=None):
        return get_object_or_404(self.model, pk=self.kwargs[self.pk_url_kwarg])

    def get_success_url(self):
        return reverse('blog:post_detail', args=[self.object.pk])


class PostDeleteView(LoginRequiredMixin, PostMixin, DeleteView):
    """Удаление поста"""

    def get_success_url(self):
        return reverse('blog:profile', args=[self.request.user.username])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=context['post'])
        return context


class CommentCreateView(LoginRequiredMixin, CreateView):
    """Страница написания комментария"""

    model = Comment
    form_class = CommentForm
    posts = None
    pk_url_kwarg = 'post_id'

    def get_success_url(self):
        return reverse(
            'blog:post_detail', kwargs={'post_id': self.kwargs['post_id']}
        )

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        return super().form_valid(form)


class CommentUpdateView(LoginRequiredMixin, CommentMixin, UpdateView,):
    """Редактирование коментария"""


class CommentDeleteView(LoginRequiredMixin, CommentMixin, DeleteView,):
    """Удаление коментария"""

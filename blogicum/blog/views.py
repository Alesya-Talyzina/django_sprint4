from django.http.response import HttpResponseRedirect
from django.db.models import Count
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)

from blog.models import Category, Comment, Post, User
from .forms import CommentForm, PostForm, ProfileForm


class PostQuerySet:
    pk_url_kwarg = 'post_id'

    def get_queryset(self):
        return Post.objects.select_related(
            'author',
            'location',
            'category'
        ).filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        ).order_by('-pub_date').all()


class CommentMixin:

    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return redirect('blog:post_detail', self.get_object().id)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']},
        )


class PostMixin:

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != self.request.user:
            return redirect('blog:post_detail', self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)


class IndexListView(PostQuerySet, ListView):
    """Главная страница"""

    paginate_by = 10
    template_name = 'blog/index.html'

    def get_queryset(self):
        return super().get_queryset().annotate(comment_count=Count('comment'))


class PostDetailView(DetailView):
    """Страница отдельного поста"""

    model = Post
    template_name = 'blog/detail.html'
    success_url = reverse_lazy('blog:index')
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        instance = self.get_object()
        if (
            (instance.author != request.user)
            and (
                not instance.is_published
                or (
                    instance.category and not instance.category.is_published
                ) or instance.pub_date > timezone.now()
            )
        ):
            return render(request, 'pages/404.html', status=404)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comment.select_related(
                'author'
            ).order_by('created_at')
        )
        context['can_edit'] = self.object.author == self.request.user
        return context

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile', kwargs={'username': self.object.author.username}
        )


class CategoryListView(ListView):
    """Страница отдельной категории."""

    template_name = 'blog/category.html'
    category = None
    paginate_by = 10

    def get_queryset(self):
        self.category = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True)

        post_list = Post.objects.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now(),
            category=self.category
        ).order_by('-pub_date').annotate(comment_count=Count('comment'))

        return post_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class ProfileListView(ListView):
    """Страница профиля пользователя"""

    model = User
    template_name = 'blog/profile.html'
    ordering = '-pub_date'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = User.objects.get(username=self.kwargs['username'])
        return context

    def get_queryset(self):
        self.author = get_object_or_404(User, username=self.kwargs['username'])
        if self.request.user.username == self.kwargs['username']:
            return Post.objects.select_related(
                'location', 'category', 'author'
            ).filter(
                author=self.author
            ).order_by('-pub_date').annotate(
                comment_count=Count('comment')
            )

        return Post.objects.select_related(
            'location', 'category', 'author'
        ).filter(
            author=self.author,
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True,
        ).order_by('-pub_date').annotate(comment_count=Count('comment'))


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
        success_url = reverse_lazy(
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
        return HttpResponseRedirect(reverse_lazy('blog:post_detail',
                                                 args=[post.pk]))

    def get_object(self, queryset=None):
        return get_object_or_404(self.model, pk=self.kwargs[self.pk_url_kwarg])

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', args=[self.object.pk])


class PostDeleteView(LoginRequiredMixin, PostMixin, DeleteView):
    """Удаление поста"""

    success_url = reverse_lazy('blog:index')

    def get_success_url(self):
        return reverse_lazy('blog:profile', args=[self.request.user.username])

    def get_object(self, queryset=None):
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, pk=post_id, author=self.request.user)
        return post

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

    pass


class CommentDeleteView(LoginRequiredMixin, CommentMixin, DeleteView,):
    """Удаление коментария"""

    pass

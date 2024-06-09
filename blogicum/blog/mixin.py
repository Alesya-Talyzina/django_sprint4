from django.db.models import Count
from django.utils import timezone
from django.shortcuts import redirect
from django.urls import reverse

from blog.models import Comment, Post
from blog.forms import CommentForm, PostForm


class PostQuerySetMixin:

    model = Post

    def get_queryset(self):
        queryset = Post.objects.select_related(
            'author',
            'location',
            'category'
        ).filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')
        return self.annotate_comment_count(queryset)

    def annotate_comment_count(self, queryset):
        return queryset.annotate(
            comment_count=Count('comments')
        )


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

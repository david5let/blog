from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from blog.models import Post, Comment
from django.views.generic import ListView, DetailView, CreateView, View, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from tasks.mixins import UserIsOwnerMixin
from tasks.forms import TaskForm, TaskFilterForm, CommentForm
from django.http import HttpResponseRedirect
from django.core.exceptions import PermissionDenied
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

# Create your views here.

def post_list(request):
    posts = Post.objects.all()
    return render(request, 'blog/post_list.html', {'posts': posts})

def post_detail(request, pk):
    post = Post.objects.get(pk=pk)
    comments = post.comments.all()
    return render(request, 'blog/post_detail.html', {'post': post, 'comments': comments})

def add_comment_to_post(request, pk):
    post = Post.objects.get(pk=pk)
    if request.method == 'POST':
        author = request.POST['author']
        text = request.POST['text']
        Comment.objects.create(post=post, author=author, text=text)
    return HttpResponseRedirect(reverse('blog:post_detail', args=[pk]))

class CommentUpdateView(LoginRequiredMixin, UpdateView):
    model = models.Comment
    fields = ['content']
    template_name = 'tasks/edit_comment.html'

    def form_valid(self, form):
        comment = self.get_object()
        if comment.author != self.request.user:
            raise PermissionDenied("Ви не можете редагувати цей коментар.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('tasks:task_detail', kwargs={'pk': self.object.task.pk})

class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = models.Comment
    template_name = 'tasks/delete_comment.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(author=self.request.user)

    def get_success_url(self):
        return reverse('tasks:task_detail', kwargs={'pk': self.object.task.pk})

class CommentLikeToggle(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        comment = get_object_or_404(models.Comment, pk=self.kwargs.get('pk'))
        like_qs = models.Like.objects.filter(comment=comment, user=request.user)
        if like_qs.exists():
            like_qs.delete()
        else:
            models.Like.objects.create(comment=comment, user=request.user)
        return HttpResponseRedirect(comment.get_absolute_url())

class CustomLoginView(LoginView):
    template_name = "tasks/login.html"
    redirect_authenticated_user = True

class CustomLogoutView(LogoutView):
    next_page = "tasks:login"

class RegisterView(CreateView):
    template_name = "tasks/register.html"
    form_class = UserCreationForm

    def form_valid(self, form):
        valid = super().form_valid(form)
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        user = authenticate(username=username, password=password)
        login(self.request, user)
        return valid
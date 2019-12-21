from .forms import SignUpForm
from django.urls import reverse_lazy
from django.shortcuts import HttpResponse
from django.views.generic import ListView, CreateView
from .models import User, Post, Comment, WorkflowLog
import json
from django.contrib.auth.mixins import LoginRequiredMixin


# Create your views here.
class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = 'signup.html'
    model = User
    success_url = reverse_lazy('login')


class PublicPostView(ListView, LoginRequiredMixin):
    template_name = 'index.html'
    model = User

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['post_objects'] = Post.objects.filter(current_status='Closed').order_by('-created_at').all()
        context['comment_objects'] = Comment.objects.all()
        return context


class MyTaskView(ListView):
    template_name = 'mytask.html'
    model = User

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['post_objects'] = Post.objects.filter(current_actor__pk=self.request.user.pk).all()

        return context


class MyPostView(ListView):
    template_name = 'mypost.html'
    model = User

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['post_objects'] = Post.objects.filter(user__pk=self.request.user.pk).all()
        return context


def create_post(request):
    if request.method == 'POST':
        post_text = request.POST.get('message')
        img_url = request.POST.get('image_url')
        # method to get parent of the request user
        request_user = request.user
        if request_user.parent is None:
            post = Post(post_text=post_text, user=request_user, image=img_url, current_actor=request_user,
                        current_status='Closed', last_actor=request_user)
        else:
            post = Post(post_text=post_text, user=request_user, image=img_url, current_actor=request_user.parent,
                        current_status='Initiated', last_actor=request_user)
        post.save()

        response_data = {'result': 'Created post successful!', 'postpk': post.pk, 'text': post.post_text
                         }

        return HttpResponse(
            json.dumps(response_data),
            content_type="application/json"
        )
    else:
        return HttpResponse(
            json.dumps({"nothing to see": "this isn't happening"}),
            content_type="application/json"
        )


def approve_post(request):
    if request.method == 'POST':
        user = request.user
        comments = request.POST.get('comments')
        post = Post.objects.get(pk=request.POST.get('post_id'))
        log = WorkflowLog(user=user, status='Approved', comments=comments, post=post)
        log.save()
        # updating post for new actor and state
        if user.parent is None:
            post.current_status = 'Closed'
            post.current_actor = user
        else:
            post.current_status = 'Approved'
            post.current_actor = user.parent

        post.last_actor = user
        post.save()

        response_data = {'result': 'Approved post successful!'}

        return HttpResponse(
            json.dumps(response_data),
            content_type="application/json"
        )


def reject_post(request):
    if request.method == 'POST':
        user = request.user
        comments = request.POST.get('comments')
        post = Post.objects.get(pk=request.POST.get('post_id'))
        log = WorkflowLog(user=user, status='Rejected', comments=comments, post=post)
        log.save()
        # updating post for new actor and state
        post.current_actor = post.last_actor
        post.current_status = 'Approved'
        post.last_actor = user
        post.save()

        response_data = {'result': 'Rejected post successful!'}

        return HttpResponse(
            json.dumps(response_data),
            content_type="application/json"
        )


def correct_post(request):
    if request.method == 'POST':
        user = request.user
        comments = request.POST.get('comments')
        post = Post.objects.get(pk=request.POST.get('post_id'))
        log = WorkflowLog(user=user, status='Correction', comments=comments, post=post)
        log.save()
        # updating post for new actor and state
        post.current_actor = user.parent
        post.current_status = 'Approved'
        post.last_actor = user
        post.save()

        response_data = {'result': 'Rejected post successful!'}

        return HttpResponse(
            json.dumps(response_data),
            content_type="application/json"
        )

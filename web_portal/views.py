from .forms import SignUpForm
from django.urls import reverse_lazy
from django.shortcuts import HttpResponse
from django.views.generic import ListView, CreateView, DetailView
from .models import *
import json
from django.contrib.auth.mixins import LoginRequiredMixin
import time
from easy_cression import settings


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
        context['length_post'] = len(Post.objects.filter(user=self.request.user).all())
        context['length_task'] = len(Post.objects.filter(current_actor=self.request.user).all())
        context['comment_objects'] = Comment.objects.all()
        all_post = len(Post.objects.all())
        my_contrib = (context['length_post'] / all_post) * 100
        avg_post_per_user = all_post / len(User.objects.all())
        context['my_contrib'] = my_contrib
        context['avg_post_per_user'] = avg_post_per_user
        return context


class MyTaskView(ListView):
    template_name = 'mytask.html'
    model = User

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['post_objects'] = Post.objects.filter(current_actor__pk=self.request.user.pk).all()
        context['length_post'] = len(Post.objects.filter(user=self.request.user).all())
        context['length_task'] = len(Post.objects.filter(current_actor=self.request.user).all())
        all_post = len(Post.objects.all())
        print(all_post)
        my_contrib = (context['length_post'] / all_post) * 100
        avg_post_per_user = all_post / len(User.objects.all())
        context['my_contrib'] = my_contrib
        context['avg_post_per_user'] = avg_post_per_user

        return context


class MyPostView(ListView):
    template_name = 'mypost.html'
    model = User

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['post_objects'] = Post.objects.filter(user__pk=self.request.user.pk).order_by('-created_at').all()
        context['length_post'] = len(Post.objects.filter(user=self.request.user).all())
        context['length_task'] = len(Post.objects.filter(current_actor=self.request.user).all())
        return context


class PostDetailView(DetailView):
    template_name = 'post-detail.html'
    model = Post

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        post = Post.objects.filter(pk=self.kwargs['pk']).first()
        context['post'] = post
        context['logs'] = WorkflowLog.objects.filter(post=post).all()
        return context


class PostActivityView(DetailView):
    template_name = 'post-activity.html'
    model = Post

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        post = Post.objects.filter(pk=self.kwargs['pk']).first()
        context['post'] = post
        context['comments'] = Comment.objects.filter(post=post).order_by('-created_at').all()
        like = PostLike.objects.filter(post=post, user=self.request.user).first()
        if like is None or like.flag:
            context['liked'] = 'true'
        else:
            context['liked'] = 'false'
        return context


def handle_uploaded_file(f, path):
    with open(settings.STATIC_URL + path, 'x') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


def create_post(request):
    if request.method == 'POST':
        try:
            post_text = request.POST.get('message')
            image = None
            if bool(request.FILES):
                image = request.FILES['image']
                request.user.image = image
                request.user.save()

                if image is not None:
                    arr = image.name.split('.')
                    image.name = str(int(round(time.time() * 1000))) + '.' + arr[(len(arr) - 1)]

            # method to get parent of the request user
            request_user = request.user
            if request_user.parent is None:
                post = Post(post_text=post_text, user=request_user, image=image, current_actor=None,
                            current_status='Closed', last_actor=request_user)
            else:
                post = Post(post_text=post_text, user=request_user, image=image, current_actor=request_user.parent,
                            current_status='Initiated', last_actor=request_user)
            post.save()

            response_data = {'result': 'Created post successful!', 'postpk': post.pk, 'text': post.post_text
                             }

            return HttpResponse(
                json.dumps(response_data),
                content_type="application/json"
            )
        except ex as exception:
            return HttpResponse(
                json.dumps(response_data),
                content_type="application/json"
            )
    else:
        return HttpResponse(
            json.dumps({"nothing to see": "this isn't happening"}),
            content_type="application/json"
        )


def post_comment(request):
    if request.method == 'POST':
        user = request.user
        comments = request.POST.get('comments')
        post = Post.objects.get(pk=request.POST.get('post_id'))
        c = Comment(user=user, comments_text=comments, post=post)
        c.save()
        response_data = {'result': 'Comment posted successfully!'}

        return HttpResponse(
            json.dumps(response_data),
            content_type="application/json"
        )


def post_sentiment(request):
    if request.method == 'POST':
        user = request.user
        liked = request.POST.get('liked')
        flag = True;
        if liked == 'true':
            flag = False
        post = Post.objects.get(pk=request.POST.get('post_id'))
        post_like = PostLike(user=user, flag=flag, post=post)
        post_like.save()
        response_data = {'result': 'Like posted successfully!'}

        return HttpResponse(
            json.dumps(response_data),
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
            post.current_actor = None
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
        post.current_status = 'Rejected'
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
        post.current_status = 'Correction'
        post.last_actor = user
        post.save()

        response_data = {'result': 'Corrected post successful!'}

        return HttpResponse(
            json.dumps(response_data),
            content_type="application/json"
        )

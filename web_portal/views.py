from .forms import SignUpForm
from django.urls import reverse_lazy
from django.shortcuts import HttpResponse
from django.views.generic import ListView, CreateView, DetailView, TemplateView
from .models import *
import json
from django.contrib.auth.mixins import LoginRequiredMixin
import time
from easy_cression import settings
from django.db.models import Q
from django.db.models import Count
from datetime import datetime
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from django.contrib.auth.decorators import login_required

# Create your views here.
class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = 'signup.html'
    model = User
    success_url = reverse_lazy('login')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['type'] = User.objects.all()

        return context


class PublicPostView(LoginRequiredMixin, ListView):
    login_url = '/login/'
    template_name = 'index.html'
    model = User

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['post_objects'] = Post.objects.filter(current_status='Closed').order_by('-created_at').all()
        post_count = len(Post.objects.filter(user=self.request.user).all())
        context['length_post'] = post_count
        context['length_task'] = len(Post.objects.filter(current_actor=self.request.user).all())
        context['comment_objects'] = Comment.objects.all()
        all_post = len(Post.objects.all())
        my_contrib = 0
        avg_post_per_user = 0
        percent = 0

        if all_post > 0:
            my_contrib = post_count
            avg_post_per_user = all_post / len(User.objects.all())
            percent = round((abs((my_contrib - avg_post_per_user)) / avg_post_per_user) * 100)

        context['my_contrib'] = my_contrib
        context['avg_post_per_user'] = round(avg_post_per_user, 2)
        context['percent'] = percent
        closed_count = Post.objects.filter(user=self.request.user, current_status='Closed').count()
        open_count = Post.objects.filter(~Q(current_status='Closed'), user=self.request.user).count()
        context['posts'] = [closed_count,
                            open_count,
                            open_count + closed_count]
        likes_map = {}
        likes = PostLike.objects.filter(user=self.request.user).all()
        for like in likes:
            likes_map[like.post.pk] = like.flag
        context['likes_map'] = likes_map
        return context


class MyTaskView(LoginRequiredMixin, ListView):
    login_url = '/login/'
    template_name = 'mytask.html'
    model = User

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['post_objects'] = Post.objects.filter(current_actor__pk=self.request.user.pk).all()
        context['length_post'] = len(Post.objects.filter(user=self.request.user).all())
        context['length_task'] = len(Post.objects.filter(current_actor=self.request.user).all())
        all_post = len(Post.objects.all())
        my_contrib = 0
        avg_post_per_user = 0
        if all_post > 0:
            my_contrib = (context['length_post'] / len(User.objects.all()))
            avg_post_per_user = all_post / len(User.objects.all())
        context['my_contrib'] = my_contrib
        context['avg_post_per_user'] = avg_post_per_user

        return context


class MyPostView(LoginRequiredMixin, ListView):
    login_url = '/login/'
    template_name = 'mypost.html'
    model = User

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['post_objects'] = Post.objects.filter(user__pk=self.request.user.pk).order_by('-created_at').all()
        context['length_post'] = len(Post.objects.filter(user=self.request.user).all())
        context['length_task'] = len(Post.objects.filter(current_actor=self.request.user).all())
        return context


class PostDetailView(LoginRequiredMixin, DetailView):
    login_url = '/login/'
    template_name = 'post-detail.html'
    model = Post

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        post = Post.objects.filter(pk=self.kwargs['pk']).first()
        # context['comments'] = Comment.objects.filter(post=post).order_by('-created_at').all()
        context['post'] = post
        context['logs'] = WorkflowLog.objects.filter(post=post).all()
        return context


class PostActivityView(LoginRequiredMixin, DetailView):
    login_url = '/login/'
    template_name = 'post-activity.html'
    model = Post

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        post = Post.objects.filter(pk=self.kwargs['pk']).first()
        context['post'] = post
        context['comments'] = Comment.objects.filter(post=post).order_by('-created_at').all()
        like = PostLike.objects.filter(post=post, user=self.request.user).first()
        if like is not None:
            context['liked'] = 'true'
        else:
            context['liked'] = 'false'
        return context


class AnalysisView(LoginRequiredMixin, TemplateView):
    login_url = '/login/'
    template_name = 'analytics.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        qs = Comment.objects.all()
        my_text = ""
        for text in qs:
            my_text += text.comments_text + ' '
        stop_words = set(stopwords.words('english'))

        word_tokens = word_tokenize(my_text)

        filtered_sentence = [w for w in word_tokens if not w in stop_words]
        comment_text = listToString(filtered_sentence)

        context['comment_text'] = comment_text

        return context


def listToString(s):
    # initialize an empty string
    str1 = ""

    # traverse in the string
    for ele in s:
        str1 += ele + " "

    # return string
    return str1


class StatsView(LoginRequiredMixin, TemplateView):
    login_url = '/login/'
    template_name = 'stats.html'
    model = Post

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        qs = (Post.objects.all().
              extra(select={
            'day': "EXTRACT(day FROM created_at)"
        }).
              values('day').
              annotate(count_items=Count('created_at')))
        # qs = qs.order_by('created_at')
        context['day_wise_posts'] = qs.order_by('created_at__day')
        qs = (Post.objects.all().
              values('user__username').
              annotate(count_items=Count('pk')))
        qs = qs.filter(created_at__month=datetime.now().month).order_by('-count_items')
        top5 = qs.all()[:5]
        context['top_performers'] = top5.all()
        context['total_posts'] = len(Post.objects.all())
        closed_count = Post.objects.filter(current_status='Closed').count()
        open_count = Post.objects.filter(~Q(current_status='Closed')).count()
        context['post_data'] = [open_count, closed_count]
        user = User.objects.all()
        table_data = []
        for _ in user:
            count_post = Post.objects.all().filter(user__pk=_.pk).count()
            count_comment = Comment.objects.all().filter(user__pk=_.pk).count()
            count_like = PostLike.objects.all().filter(user__pk=_.pk).count() + CommentLike.objects.all().filter(
                user__pk=_.pk).count()
            table = {"user": _.username, "count_post": count_post, "count_comment": count_comment,
                     "count_like": count_like}
            table_data.append(table)
        context["table_data"] = table_data
        return context


def handle_uploaded_file(f, path):
    with open(settings.STATIC_URL + path, 'x') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

@login_required(login_url='/login/')
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


@login_required(login_url='/login/')
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


@login_required(login_url='/login/')
def post_sentiment(request):
    if request.method == 'POST':
        user = request.user
        liked = request.POST.get('liked')
        flag = True
        if liked == 'true':
            flag = False
        post = Post.objects.get(pk=request.POST.get('post_id'))
        post_like = PostLike.objects.filter(user=user, post=post)
        if post_like.exists():
            post_like.update(flag=flag)
        else:
            post_like = PostLike(user=user, post=post, flag=True)
            post_like.save()

        response_data = {'result': 'Like posted successfully!'}

        return HttpResponse(
            json.dumps(response_data),
            content_type="application/json"
        )


@login_required(login_url='/login/')
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


@login_required(login_url='/login/')
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


@login_required(login_url='/login/')
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

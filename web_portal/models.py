from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    TYPE_CHOICES = (
            ('1', 'BA'),
            ('2', 'Sup'),
            ('3', 'Man'),
            ('4', 'Exec')
        )
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='BA')
    parent = models.ForeignKey('self',on_delete=models.CASCADE, null=True, blank=True)

class Post(models.Model):
    TYPE_CHOICES = (
        ('Initiated', 'Initiated'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Correction', 'Correction'),
        ('Closed', 'Closed')
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post_title = models.CharField(max_length=100)
    post_text = models.TextField()
    image = models.ImageField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    current_actor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='current_actor',default=0)
    last_actor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='last_actor',default=0)
    current_status = models.CharField(max_length=10, choices=TYPE_CHOICES, default='Initiated')

    class Meta:
        db_table = 'post'
        verbose_name = 'post'
        verbose_name_plural = 'posts'


class PostLike(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    flag = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'post_like'
        verbose_name = 'post like'
        verbose_name_plural = 'post like'


class WorkflowLog(models.Model):
    TYPE_CHOICES = (
        ('Initiated', 'Initiated'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Correction', 'Correction'),
        ('Closed', 'Closed')
    )
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=TYPE_CHOICES, default='Initiated')
    comments = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    comments_text = models.TextField()
    reply = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def replys(self):
        return self.reply.comments_text

    class Meta:
        db_table = 'comment'
        verbose_name = 'comment'
        verbose_name_plural = 'comments'


class CommentLike(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    flag = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'comment_like'
        verbose_name = 'comment like'
        verbose_name_plural = 'comment like'


from django.urls import path
from django.contrib.auth import views as  auth_views
from .views import *
from easy_cression import settings
from django.conf.urls.static import static
urlpatterns = [

    # create user with sign up form
    path('signup/', SignUpView.as_view(), name='signup'),
    # Login
    path('login/', auth_views.LoginView.as_view(redirect_authenticated_user=True, template_name='login_new.html'),
         name='login'),
    # Logout
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('myposts/', MyPostView.as_view(), name="myposts"),
    path('mytasks/', MyTaskView.as_view(), name="mytasks"),
    path('public_posts/', PublicPostView.as_view(), name="public_posts"),
    path('', PublicPostView.as_view(), name="home"),
    path('posts/', create_post, name="create_post"),
    path('comments/', post_comment, name="post_comment"),
    path('sentiment/', post_sentiment, name="post_sentiment"),
    path('posts/<int:pk>/', PostDetailView.as_view(), name="post-details"),
    path('activities/<int:pk>/', PostActivityView.as_view(), name="post-activities"),
    path('reject/', reject_post, name="reject"),
    path('approve/', approve_post, name="approve"),
    path('correct/', correct_post, name="correct"),

]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

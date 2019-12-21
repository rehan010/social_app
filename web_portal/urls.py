from django.urls import path
from django.contrib.auth import views as  auth_views
from .views import SignUpView ,create_post,correct_post,reject_post,approve_post,MyPostView,PublicPostView,MyTaskView

urlpatterns = [

    # create user with sign up form
    path('signup/', SignUpView.as_view(), name='signup'),
    # Login
    path('login/', auth_views.LoginView.as_view(redirect_authenticated_user=True, template_name='login.html'),
         name='login'),
    # Logout
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    path('myposts/', MyPostView.as_view(), name="myposts"),
    path('mytasks/', MyTaskView.as_view(), name="mytasks"),
    path('public_posts/', PublicPostView.as_view(), name="public_posts"),
    path('posts/', create_post, name="create_post"),
    path('reject/', reject_post, name="reject"),
    path('approve/', approve_post, name="approve"),
    path('correct/', correct_post, name="correct"),

]

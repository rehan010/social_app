from django.contrib import admin
from .models import User
from .models import User , Post ,Comment,PostLike,CommentLike , WorkflowLog

# Register your models here.
admin.site.site_header = 'Social Network admin'
admin.site.site_title = 'Social Network admin'
admin.site.site_url = 'http://SocialNetwork.com/'
admin.site.index_title = 'Social Network Administration'
admin.empty_value_display = '**Empty**'

class UserAdmin(admin.ModelAdmin):

    list_display = ('username','first_name','email','parent')
class PostAdmin(admin.ModelAdmin):
    list_display = ('user','post_text', 'created_at', 'updated_at')

class PostLikeAdmin(admin.ModelAdmin):
    list_display = ('user','post','flag','created_at', 'updated_at')

class CommentAdmin(admin.ModelAdmin):
    list_display = ('user','post', 'comments_text','created_at', 'updated_at')

class CommentLikeAdmin(admin.ModelAdmin):
    list_display = ('user','comment','flag','created_at', 'updated_at')

class WorkflowLogAdmin(admin.ModelAdmin):
    list_display = ('user','post','status','created_at', 'updated_at')


admin.site.register(Post,PostAdmin)
admin.site.register(PostLike,PostLikeAdmin)
admin.site.register(Comment,CommentAdmin)
admin.site.register(CommentLike,CommentLikeAdmin)
admin.site.register(WorkflowLog,WorkflowLogAdmin)
admin.site.register(User,UserAdmin)


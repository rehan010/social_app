from django.contrib import admin
from .models import User
from .models import User , Post ,Comment,PostLike,CommentLike , WorkflowLog
from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from django.utils.translation import ugettext_lazy as _
# Register your models here.
admin.site.site_header = 'Social Network admin'
admin.site.site_title = 'Social Network admin'
admin.site.site_url = 'http://SocialNetwork.com/'
admin.site.index_title = 'Social Network Administration'
admin.empty_value_display = '**Empty**'

class UserCreationForm(forms.ModelForm):

    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    password_confirm = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        exclude = ('is_active',)

    def clean_password_confirm(self):

        password = self.cleaned_data.get("password")
        password_confirm = self.cleaned_data.get("password_confirm")
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Passwords don't match")
        return


    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

class UserChangeForm(forms.ModelForm):

    password = ReadOnlyPasswordHashField(label=_("Password"),
                                         help_text=_("Raw passwords are not stored, so there is no way to see "
                                                     "this user's password, but you can change the password "
                                                     "using <a href=\"../password/\">this form</a>."))

    class Meta:
        model = User
        exclude = ('is_admin',)

    def clean_password(self):
        return self.initial["password"]

class UserAdmin(BaseUserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm

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


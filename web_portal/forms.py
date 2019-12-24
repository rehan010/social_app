from django.contrib.auth.forms import UserCreationForm
from .models import User
from django import forms

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    last_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

    type = forms.ChoiceField(
        choices=User.TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}))

    # parent = forms.ChoiceField( widget=forms.Select(attrs={'class': 'form-control'}))


    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email','type','parent')




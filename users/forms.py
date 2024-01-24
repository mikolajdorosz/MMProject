from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import Face

class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class AddFaceForm(forms.ModelForm):
    class Meta:
        model = Face
        fields = ['user', 'name', 'picture']

    def __init__(self, user, *args, **kwargs):
        super(AddFaceForm, self).__init__(*args, **kwargs)
        self.fields['user'].initial = user
        self.fields['user'].widget = forms.HiddenInput()
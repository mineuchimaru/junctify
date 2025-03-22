# music/forms.py
from django import forms
from django.contrib.auth import get_user_model
from .models import Profile,Track,Junction,Comment

User = get_user_model()

class TrackForm(forms.ModelForm):
    class Meta:
        model = Track
        fields = ['title', 'type', 'audio_file', 'image_file', 'description']
        widgets = {
            'type': forms.Select(attrs={'id': 'id_type'}),
            'audio_file': forms.FileInput(attrs={'id': 'id_audio_file'}),
            'image_file': forms.FileInput(attrs={'id': 'id_image_file'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['audio_file'].required = False
        self.fields['image_file'].required = False

class JunctionForm(forms.ModelForm):
    class Meta:
        model = Junction
        fields = ['title', 'type', 'audio_file', 'image_file', 'description']
        widgets = {
            'type': forms.Select(attrs={'id': 'id_type'}),
            'audio_file': forms.FileInput(attrs={'id': 'id_audio_file'}),
            'image_file': forms.FileInput(attrs={'id': 'id_image_file'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['audio_file'].required = False
        self.fields['image_file'].required = False

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['icon']

class UsernameChangeForm(forms.Form):
    new_username = forms.CharField(max_length=150, label="New Username")

class EmailChangeForm(forms.Form):
    new_email = forms.EmailField(label="New Email")

class PasswordChangeForm(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput, label="New Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

class UserChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username']

class EmailChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email']

class ProfileIconForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['icon']
        widgets = {
            'icon': forms.FileInput(),
        }

class ProfileBioForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio']

class TrackForm(forms.ModelForm):
    class Meta:
        model = Track
        fields = ['title', 'type', 'audio_file', 'image_file', 'description']
        widgets = {
            'type': forms.Select(attrs={'id': 'id_type'}),
            'audio_file': forms.FileInput(attrs={'id': 'id_audio_file'}),
            'image_file': forms.FileInput(attrs={'id': 'id_image_file'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['audio_file'].required = False
        self.fields['image_file'].required = False
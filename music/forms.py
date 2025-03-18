# music/forms.py
from django import forms
from django.contrib.auth import get_user_model
from .models import Profile,Track

User = get_user_model()

class UsernameChangeForm(forms.Form):
    new_username = forms.CharField(max_length=150, required=True)

class EmailChangeForm(forms.Form):
    new_email = forms.EmailField(required=True)

class PasswordChangeForm(forms.Form):
    current_password = forms.CharField(widget=forms.PasswordInput, required=True)
    new_password1 = forms.CharField(widget=forms.PasswordInput, required=True)
    new_password2 = forms.CharField(widget=forms.PasswordInput, required=True)

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean(self):
        cleaned_data = super().clean()
        current_password = cleaned_data.get('current_password')
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')

        if current_password and not self.user.check_password(current_password):
            raise forms.ValidationError("Current password is incorrect.")
        if new_password1 and new_password2 and new_password1 != new_password2:
            raise forms.ValidationError("New passwords do not match.")
        return cleaned_data

# アイコン専用のフォーム
class IconForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['icon']
        widgets = {
            'icon': forms.ClearableFileInput(),
        }

# Bio専用のフォーム
class BioForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3}),
        }

class MusicPostForm(forms.ModelForm):
    class Meta:
        model = Track
        fields = ['title', 'audio_file', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'audio_file': forms.ClearableFileInput(),
        }
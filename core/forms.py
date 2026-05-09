from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from .models import DatasetUpload


class UserRegistrationForm(forms.ModelForm):
    mobile = forms.CharField(max_length=20, required=True)
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error("confirm_password", "Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.is_active = False
        if commit:
            user.save()
            mobile = self.cleaned_data.get("mobile")
            from .models import UserProfile

            UserProfile.objects.create(user=user, mobile=mobile)
        return user


class DatasetUploadForm(forms.ModelForm):
    class Meta:
        model = DatasetUpload
        fields = ["file"]


class PredictionForm(forms.Form):
    feature1 = forms.FloatField(label="Feature 1")
    feature2 = forms.FloatField(label="Feature 2")
    feature3 = forms.FloatField(label="Feature 3")
    feature4 = forms.FloatField(label="Feature 4")
    feature5 = forms.FloatField(label="Feature 5")
    feature6 = forms.FloatField(label="Feature 6")


class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Login ID")
    password = forms.CharField(widget=forms.PasswordInput)

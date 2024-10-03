from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'placeholder': 'Username'}),
        label='Username'
    )
    password = forms.CharField(
        max_length=128,
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'}),
        label='Password'
    )

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        # Add custom validation if necessary
        if not username or not password:
            raise forms.ValidationError("Both fields are required.")

        return cleaned_data

class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    
    def clean_first_name(self):
        username = self.cleaned_data.get('username')
        if len(username) < 2:
            raise forms.ValidationError("First name must be at least 2 characters long.")
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists")
        return email
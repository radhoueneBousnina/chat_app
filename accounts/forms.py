from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm

User = get_user_model()


class RegisterForm(forms.ModelForm):
    first_name = forms.CharField(required=True, max_length=30)
    last_name = forms.CharField(required=True, max_length=30)
    email = forms.EmailField(required=True, max_length=75)
    password = forms.CharField(required=True, widget=forms.PasswordInput)
    confirm_password = forms.CharField(required=True, widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")

        return cleaned_data


class LoginForm(AuthenticationForm):
    username = forms.CharField(required=True)

    def clean(self):
        email = self.cleaned_data.get('username')
        try:
            user = User.objects.get(username=email)
            self.cleaned_data['username'] = user.username
        except User.DoesNotExist:
            raise forms.ValidationError("Invalid email or password")
        return super().clean()

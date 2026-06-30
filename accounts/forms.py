from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class RegisterForm(forms.Form):
    username = forms.CharField(label=_("Имя пользователя"), min_length=3, max_length=50)
    email = forms.EmailField(label=_("Email"))
    password = forms.CharField(label=_("Пароль"), widget=forms.PasswordInput)
    confirm_password = forms.CharField(label=_("Подтвердите пароль"), widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            is_password = isinstance(field.widget, forms.PasswordInput)
            field.widget.attrs["class"] = "input pr-11" if is_password else "input"

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError(_("Пользователь с таким именем уже существует."))
        return username

    def clean_email(self):
        email = self.cleaned_data["email"].strip()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(_("Пользователь с таким email уже существует."))
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError(_("Пароли не совпадают."))
        return cleaned_data


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            is_password = isinstance(field.widget, forms.PasswordInput)
            field.widget.attrs["class"] = "input pr-11" if is_password else "input"

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if user.is_banned:
            raise forms.ValidationError(_("Этот аккаунт заблокирован."), code="banned")

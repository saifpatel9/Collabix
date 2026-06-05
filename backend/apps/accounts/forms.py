import re

from django.contrib.auth.forms import (
    AuthenticationForm,
    ReadOnlyPasswordHashField,
    PasswordChangeForm,
    SetPasswordForm,
)
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import User


INPUT_CLASS = (
    "w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm "
    "text-slate-900 outline-none transition focus:border-cyan-500 focus:ring-4 "
    "focus:ring-cyan-100 dark:border-slate-700 dark:bg-slate-950 dark:text-white"
)


def validate_password_strength(password, user_email=None):
    errors = []
    if len(password) < 8:
        errors.append(_("Password must be at least 8 characters long."))
    if not re.search(r"[A-Z]", password):
        errors.append(_("Password must contain at least one uppercase letter."))
    if not re.search(r"[0-9]", password):
        errors.append(_("Password must contain at least one number."))
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        errors.append(_("Password must contain at least one special character."))
    if user_email and password.lower() in user_email.lower():
        errors.append(_("Password cannot be too similar to your email address."))

    if errors:
        raise ValidationError(errors)


class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": INPUT_CLASS, "placeholder": "Current Password"}
        )
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": INPUT_CLASS, "placeholder": "New Password"}
        )
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": INPUT_CLASS, "placeholder": "Confirm New Password"}
        )
    )

    def clean_new_password1(self):
        password1 = self.cleaned_data.get("new_password1")
        validate_password_strength(password1, user_email=self.user.email)
        return password1


class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": INPUT_CLASS, "placeholder": "New Password"}
        )
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": INPUT_CLASS, "placeholder": "Confirm New Password"}
        )
    )

    def clean_new_password1(self):
        password1 = self.cleaned_data.get("new_password1")
        validate_password_strength(password1, user_email=self.user.email)
        return password1


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={"class": INPUT_CLASS, "placeholder": "your@email.com"}
        )
    )


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ("email", "full_name", "role", "department", "phone")

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = (
            "email",
            "password",
            "full_name",
            "role",
            "department",
            "phone",
            "is_active",
            "is_staff",
        )


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label="Email address",
        widget=forms.EmailInput(
            attrs={
                "class": INPUT_CLASS,
                "autocomplete": "email",
                "placeholder": "you@company.com",
            }
        ),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": INPUT_CLASS,
                "autocomplete": "current-password",
                "placeholder": "Password",
            }
        )
    )
    remember = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={"class": "checkbox-input"}),
    )


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("full_name", "phone", "profile_image")
        widgets = {
            "full_name": forms.TextInput(attrs={"class": INPUT_CLASS}),
            "phone": forms.TextInput(attrs={"class": INPUT_CLASS}),
            "profile_image": forms.ClearableFileInput(
                attrs={
                    "class": "w-full rounded-2xl border border-dashed border-slate-300 bg-white px-4 py-3 text-sm dark:border-slate-700 dark:bg-slate-950"
                }
            ),
        }

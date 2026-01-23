from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AdminUserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError

from utils.validators import UsernameValidator, NameValidator


User = get_user_model()


class CustomUserCreationForm(AdminUserCreationForm):
    class Meta:
        model = User
        fields = AdminUserCreationForm.Meta.fields + ('phone_number', 'image',)


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = UserChangeForm.Meta.fields


class UserBaseForm(forms.Form):
    username = forms.CharField(
        max_length=30,
        label='',
        validators=[UsernameValidator()],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username...',
        }),
    )
    email = forms.EmailField(
        label='',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email Address...',
        }),
    )
    first_name = forms.CharField(
        max_length=15,
        label='',
        validators=[NameValidator('First Name')],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'FirstName...',
        }),
    )
    last_name = forms.CharField(
        max_length=15,
        label='',
        validators=[NameValidator('Last Name')],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'LastName...',
        }),
    )
    phone_number = forms.CharField(
        max_length=15,
        label='',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Phone Number...',
        }),
    )


class RegisterForm(UserBaseForm):
    password = forms.CharField(
        max_length=128,
        min_length=4,
        label='',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password...',
        }),
    )
    confirm_password = forms.CharField(
        max_length=128,
        min_length=4,
        label='',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm Password...',
        }),
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')

        if User.objects.filter(username=username).exists():
            raise ValidationError('This username already exists.')
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')

        if User.objects.filter(email=email).exists():
            raise ValidationError('This email address already exists.')
        return email
    
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')

        if User.objects.filter(phone_number=phone_number).exists():
            raise ValidationError('This phone number already exists.')
        return phone_number

    def clean(self):
        cd = self.cleaned_data
        password = cd.get('password')
        confirm_password = cd.get('confirm_password')

        if password != confirm_password:
            raise ValidationError("Passwords didn't match.")


class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=30,
        label='',
        validators=[UsernameValidator()],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username...',
        }),
    )
    password = forms.CharField(
        max_length=128,
        min_length=4,
        label='',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password...',
        }),
    )


class AccountEditForm(UserBaseForm):
    image = forms.ImageField(
        label='',
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'placeholder': 'Profile Image...',
        }),
    )


class AccountDeleteForm(forms.Form):
    username = forms.CharField(
        max_length=30,
        label='',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username...',
        }),
    )


class ResetPasswordForm(forms.Form):
    password = forms.CharField(
        max_length=128,
        min_length=4,
        label='',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'New Password...',
        }),
    )
    confirm_password = forms.CharField(
        max_length=128,
        min_length=4,
        label='',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm Password...',
        }),
    )

    def clean(self):
        cd = self.cleaned_data
        password = cd.get('password')
        confirm_password = cd.get('confirm_password')

        if password != confirm_password:
            raise ValidationError("Passwords didn't match.")

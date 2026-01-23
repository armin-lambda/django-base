import os
import random

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.views import View

from utils.mixins import AnonymousRequiredMixin, SelfForbiddenRequiredMixin
from utils.pagination import get_pagination_context
from utils.base import send_otp_code
from .models import Relation
from .forms import (
    RegisterForm,
    LoginForm,
    AccountEditForm,
    AccountDeleteForm,
    ResetPasswordForm,
)


User = get_user_model()


class RegisterView(AnonymousRequiredMixin, View):
    template_name = 'accounts/register.html'
    form_class = RegisterForm
    
    def get(self, request):
        return render(request, self.template_name, {
            'form': self.form_class(),
        })
    
    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            cd = form.cleaned_data
            user = User.objects.create_user(username=cd['username'], email=cd['email'], password=cd['password'])
            user.first_name = cd['first_name']
            user.last_name = cd['last_name']
            user.phone_number = cd['phone_number']
            user.save()
            messages.success(request, 'Successfully registered.', 'success')
            return redirect('accounts:login')
        return render(request, self.template_name, {
            'form': form,
        })


class LoginView(AnonymousRequiredMixin, View):
    template_name = 'accounts/login.html'
    form_class = LoginForm

    def get(self, request):
        return render(request, self.template_name, {
            'form': self.form_class(),
        })
    
    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request, username=cd['username'], password=cd['password'])

            if user is not None:
                login(request, user)
                messages.success(request, 'Successfully logged in.', 'success')
                return redirect('index')
            messages.error(request, 'Incorrect Username or Password.', 'danger')
            return redirect('accounts:login')
        return render(request, self.template_name, {
            'form': form,
        })


class LogoutView(LoginRequiredMixin, View):
    def get(self, request):
        logout(request)
        messages.success(request, 'Successfully logged out.', 'success')
        return redirect('index')


# ----- RESET PASSWORD -----

class SendOTPCodeView(AnonymousRequiredMixin, View):
    template_name = 'accounts/send_otp_code.html'

    def get(self, request):
        return render(request, self.template_name)
    
    def post(self, request):
        username = request.POST.get('username')

        if User.objects.filter(username=username).exists():
            user = get_object_or_404(User, username=username)
            otp_code = f"{random.randint(1000, 9999)}"
            send_otp_code(user.phone_number, otp_code)

            # Just in Dev.
            print(f"\n\n{user.phone_number} - {otp_code}\n\n")

            request.session['username'] = username
            request.session['phone_number'] = user.phone_number
            request.session['otp_code'] = otp_code

            messages.success(request, 'Successfully sent you a code.', 'success')
            return redirect('accounts:verify_otp_code')
        messages.error(request, 'There is no user with this username.', 'danger')
        return redirect('accounts:send_otp_code')


class VerifyOTPCodeView(AnonymousRequiredMixin, View):
    template_name = 'accounts/verify_otp_code.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('phone_number'):
            return redirect('accounts:send_otp_code')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        return render(request, self.template_name)
    
    def post(self, request):
        input_otp_code = request.POST.get('otp_code')
        real_otp_code = request.session.get('otp_code')

        if input_otp_code == real_otp_code:
            request.session['otp_code_verified'] = True
            messages.success(request, 'Successfully verified the code.', 'success')
            return redirect('accounts:reset_password')
        messages.error(request, 'Incorrect code.', 'danger')
        return redirect('accounts:reset_password')


class ResetPasswordView(AnonymousRequiredMixin, View):
    template_name = 'accounts/reset_password.html'
    form_class = ResetPasswordForm

    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('otp_code_verified'):
            return redirect('accounts:verify_otp_code')
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        return render(request, self.template_name, {
            'form': self.form_class(),
        })
    
    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            cd = form.cleaned_data
            username = request.session.get('username')

            user = get_object_or_404(User, username=username)
            user.set_password(cd['password'])
            user.save()

            del request.session['phone_number']
            del request.session['otp_code']
            del request.session['otp_code_verified']
            del request.session['username']

            messages.success(request, 'Successfully reset your password.', 'success')
            return redirect('accounts:login')
        return render(request, self.template_name, {
            'form': form,
        })  

# ----- END RESET PASSWORD -----


class AccountEditView(LoginRequiredMixin, View):
    template_name = 'accounts/edit.html'
    form_class = AccountEditForm

    def get(self, request):
        user = request.user
        return render(request, self.template_name, {
            'form': self.form_class(initial={
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'phone_number': user.phone_number,
            }),
        })
    
    def post(self, request):
        form = self.form_class(request.POST, request.FILES)

        if form.is_valid():
            cd = form.cleaned_data
            user = request.user

            if User.objects.filter(username=cd['username']).exclude(username=user.username).exists():
                form.add_error('username', 'This username already exists.')
            if User.objects.filter(email=cd['email']).exclude(email=user.email).exists():
                form.add_error('email', 'This email address already exists.')
            if User.objects.filter(phone_number=cd['phone_number']).exclude(phone_number=user.phone_number).exists():
                form.add_error('phone_number', 'This phone number already exists.')
            else:
                user.username = cd['username']
                user.email = cd['email']
                user.first_name = cd['first_name']
                user.last_name = cd['last_name']
                user.phone_number = cd['phone_number']

                if cd['image'] is not None:
                    if user.image:
                        os.remove(user.image.path)
                        user.image.delete()
                    user.image = cd['image']
                
                user.save()
                messages.success(request, 'Successfully edited account.', 'success')
                return redirect(user.get_profile_url())
        return render(request, self.template_name, {
            'form': form,
        })


class AccountDeleteView(LoginRequiredMixin, View):
    template_name = 'accounts/delete.html'
    form_class = AccountDeleteForm

    def get(self, request):
        return render(request, self.template_name, {
            'form': self.form_class(),
        })
    
    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            cd = form.cleaned_data
            user = request.user

            if cd['username'] == user.username:
                if user.image:
                    os.remove(user.image.path)
                    user.image.delete()
                user.delete()
                messages.success(request, 'Successfully deleted account.', 'success')
                return redirect('index')
            form.add_error('username', 'Wrong username.')
        return render(request, self.template_name, {
            'form': form,
        })


class ProfileImageDeleteView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user

        if user.image:
            os.remove(user.image.path)
            user.image.delete()
            messages.success(request, 'Successfully deleted profile image.', 'success')
        return redirect(user.get_profile_url())


class PeopleView(LoginRequiredMixin, View):
    template_name = 'accounts/people.html'

    def get(self, request):
        users = User.objects.all()

        if request.GET.get('search'):
            search = request.GET.get('search')
            users = users.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )

        return render(request, self.template_name, {
            'page_obj': get_pagination_context(request, users, 10),
        })


class ProfileView(LoginRequiredMixin, View):
    template_name = 'accounts/profile.html'

    def get(self, request, **kwargs):
        user = get_object_or_404(User, username=kwargs['username'])
        return render(request, self.template_name, {
            'user': user,
            'is_followed': Relation.objects.filter(from_user=request.user, to_user=user).exists(),
        })


class FollowView(LoginRequiredMixin, SelfForbiddenRequiredMixin, View):
    def get(self, request, **kwargs):
        user = get_object_or_404(User, username=kwargs['username'])

        if not Relation.objects.filter(from_user=request.user, to_user=user).exists():
            Relation.objects.create(from_user=request.user, to_user=user)
            messages.success(request, 'Successfully followed.', 'success')
        return redirect(user.get_profile_url())


class UnfollowView(LoginRequiredMixin, SelfForbiddenRequiredMixin, View):
    def get(self, request, **kwargs):
        user = get_object_or_404(User, username=kwargs['username'])
        relation = Relation.objects.filter(from_user=request.user, to_user=user)

        if relation.exists():
            relation.delete()
            messages.success(request, 'Successfully unfollowed.', 'success')
        return redirect(user.get_profile_url())


class FollowersView(LoginRequiredMixin, View):
    template_name = 'accounts/followers.html'

    def get(self, request, **kwargs):
        user = get_object_or_404(User, username=kwargs['username'])
        followers = user.get_followers()

        if request.GET.get('search'):
            search = request.GET.get('search')
            followers = followers.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )

        return render(request, self.template_name, {
            'user': user,
            'page_obj': get_pagination_context(request, followers, 10),
        })


class FollowingView(LoginRequiredMixin, View):
    template_name = 'accounts/following.html'

    def get(self, request, **kwargs):
        user = get_object_or_404(User, username=kwargs['username'])
        following = user.get_following()

        if request.GET.get('search'):
            search = request.GET.get('search')
            following = following.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )

        return render(request, self.template_name, {
            'user': user,
            'page_obj': get_pagination_context(request, following, 10),
        })

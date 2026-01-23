from django.contrib.auth import get_user_model
from django.shortcuts import redirect, get_object_or_404


User = get_user_model()


class AnonymousRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('index')
        return super().dispatch(request, *args, **kwargs)


class SelfForbiddenRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        user = get_object_or_404(User, username=kwargs['username'])
        if request.user == user:
            return redirect('index')
        return super().dispatch(request, *args, **kwargs)
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .models import Relation
from .forms import CustomUserCreationForm, CustomUserChangeForm


User = get_user_model()


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    list_display = ['username', 'email', 'first_name', 'last_name', 'phone_number', 'is_staff']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'groups']
    add_fieldsets = UserAdmin.fieldsets + (
        (
            'Personal Info', {
                'fields': ('phone_number', 'image',)
            }
        ),
    )
    fieldsets = UserAdmin.fieldsets + (
        (
            'Personal Info', {
                'fields': ('phone_number', 'image')
            }
        ),
    )


@admin.register(Relation)
class RelationAdmin(admin.ModelAdmin):
    list_display = ['id', 'from_user', 'to_user', 'created_at']
    list_filter = ['from_user', 'to_user', 'created_at']
    search_fields = ['from_user', 'to_user']

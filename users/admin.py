#users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from .models import CoachProfile, ClientAssignment
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = [
        "email",
        "username",
        "age",
        "is_staff",
    ]
    fieldsets = UserAdmin.fieldsets + ((None, {"fields": ("age",)}),)
    add_fieldsets = UserAdmin.add_fieldsets + ((None, {"fields": ("age",)}),)


admin.site.register(CustomUser, CustomUserAdmin)


@admin.register(CoachProfile)
class CoachProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialization', 'years_of_experience')
    search_fields = ('user__username', 'specialization')
    list_filter = ('years_of_experience',)

@admin.register(ClientAssignment)
class ClientAssignmentAdmin(admin.ModelAdmin):
    list_display = ('coach', 'client', 'date_assigned', 'is_active')
    list_filter = ('is_active', 'date_assigned')
    search_fields = ('coach__username', 'client__username')

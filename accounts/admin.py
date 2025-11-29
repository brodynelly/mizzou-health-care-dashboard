from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser, Role


class CustomUserAdmin(UserAdmin):
    list_display = ('id', 'email', 'first_name', 'last_name', 'profession', 'role', 'primary_geocode')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'profession', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Location', {"fields": ("primary_geocode",)})
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'role', 'is_superuser', 'password1', 'password2', 'primary_geocode'),
        }),
    )
    search_fields = ['email', 'first_name', 'last_name']

    def save_model(self, request, obj, form, change):
        # Auto-fill profession based on role when saving from the admin
        if obj.role:
            role_to_profession = {
                'doctor': 'Medical Doctor',
                'nurse': 'Nurse'
            }
            obj.profession = role_to_profession.get(obj.role.name, obj.profession)
        super().save_model(request, obj, form, change)


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Role)

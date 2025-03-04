from django.contrib import admin
from .models import Blog
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Profile

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'author__username')
    actions = ['approve_blogs']

    def approve_blogs(self, request, queryset):
        queryset.update(status='approved')
    approve_blogs.short_description = "Approve selected blogs"





from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Profile

class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'full_name', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('email', 'username', 'full_name')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')
    ordering = ('date_joined',)

    readonly_fields = ('date_joined',)  # Mark date_joined as read-only

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('username', 'full_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),  # Keep date_joined here but make it read-only
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'full_name', 'password1', 'password2', 'is_staff', 'is_superuser')}
        ),
    )

admin.site.register(CustomUser, CustomUserAdmin)


# Register Profile Model
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'location')
    search_fields = ('user__username', 'user__email', 'location')

admin.site.register(Profile, ProfileAdmin)
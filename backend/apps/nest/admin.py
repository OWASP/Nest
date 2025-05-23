from django.contrib import admin
from apps.nest.models.user import User
# Register your models here.
class UserAdmin(admin.ModelAdmin):
    search_fields = ("username", "email")
    list_display = ("name", "github_profile", "avatar_url", "github_id","email")
    ordering = ("username",)

admin.site.register(User, UserAdmin)
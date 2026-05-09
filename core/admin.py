from django.contrib import admin

from .models import DatasetUpload, UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "mobile", "status", "activated_at")
    search_fields = ("user__username", "user__email", "mobile")


@admin.register(DatasetUpload)
class DatasetUploadAdmin(admin.ModelAdmin):
    list_display = ("name", "uploaded_by", "uploaded_at")
    search_fields = ("name", "uploaded_by__username")

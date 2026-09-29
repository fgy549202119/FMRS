from django.contrib import admin
from .models import Announcement

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'publisher', 'publish_time', 'created_at']
    list_filter = ['publish_time']
    search_fields = ['title', 'content']

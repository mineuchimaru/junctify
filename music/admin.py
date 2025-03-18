# music/admin.py
from django.contrib import admin
from .models import Track, Profile

@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'audio_file', 'uploaded_at', 'play_count')  # 表示するフィールド
    list_filter = ('artist', 'uploaded_at')  # フィルタ
    search_fields = ('title', 'artist__username')  # 検索可能フィールド

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'icon', 'bio')
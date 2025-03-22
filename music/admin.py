from django.contrib import admin
from .models import Track, Junction, Profile, Comment

# Track モデルを登録
@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'type', 'uploaded_at')
    list_filter = ('type', 'uploaded_at')
    search_fields = ('title', 'artist__username')

# Junction モデルを登録
@admin.register(Junction)
class JunctionAdmin(admin.ModelAdmin):
    list_display = ('title', 'collaborator', 'type', 'created_at')
    list_filter = ('type', 'created_at')
    search_fields = ('title', 'collaborator__username')

# Profile モデルを登録
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user__username',)

# Comment モデルを登録
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_content_object', 'text', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'text')

    def get_content_object(self, obj):
        try:
            return str(obj.content_object) if obj.content_object else "N/A"
        except Exception as e:
            return f"Error: {str(e)}"
    get_content_object.short_description = 'Content Object'
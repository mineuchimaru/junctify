from django.contrib import admin
from allauth.socialaccount.models import SocialApp

@admin.register(SocialApp)
class SocialAppAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False  # 追加を禁止

    def has_change_permission(self, request, obj=None):
        return False  # 変更を禁止

    def has_delete_permission(self, request, obj=None):
        return False  # 削除を禁止
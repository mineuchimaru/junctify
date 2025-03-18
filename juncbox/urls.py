# juncbox/urls.py
from django.contrib import admin
from django.urls import path, include
from music.views import CustomLoginView, CustomSignupView, CustomPasswordResetView, CustomPasswordResetDoneView  # カスタムビューをインポート

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('music.urls')),
    path('accounts/login/', CustomLoginView.as_view(), name='account_login'),  # カスタムログイン
    path('accounts/signup/', CustomSignupView.as_view(), name='account_signup'),  # カスタムサインアップ
    path('accounts/password/reset/', CustomPasswordResetView.as_view(), name='account_reset_password'),
    path('accounts/password/reset/done/', CustomPasswordResetDoneView.as_view(), name='account_reset_password_done'),
    path('accounts/', include('allauth.urls')),  # allauthの他のURL
]
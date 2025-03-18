# music/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.music_list, name='music_list'),
    path('music_list/', views.music_list, name='music_list'),
    path('profile/', views.profile, name='profile'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('upload/', views.upload_music, name='upload_music'),
    path('user/<str:username>/', views.user_profile, name='user_profile'),
    path('delete/<int:track_id>/', views.delete_track, name='delete_track'),
    path('good/<int:track_id>/', views.good_track, name='good_track'),
    path('play/<int:track_id>/', views.play_track, name='play_track'),
    path('comment/<int:track_id>/', views.comment_track, name='comment_track'),
    path('delete-comment/<int:comment_id>/', views.delete_comment, name='delete_comment'),
    path('logout/', views.logout, name='logout'),  # カスタムログアウトビュー
]
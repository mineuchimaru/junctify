from django.urls import path
from . import views

urlpatterns = [
    path('', views.music_list, name='music_list'),
    path('upload/', views.upload_music, name='upload_music'),
    path('profile/', views.profile, name='profile'),
    path('user/<str:username>/', views.user_profile, name='user_profile'),
    path('play/<int:track_id>/', views.play_track, name='play_track'),
    path('good/<str:content_type>/<int:content_id>/', views.good_track, name='good_track'),
    path('comment/<str:content_type>/<int:content_id>/', views.add_comment, name='add_comment'),
    path('delete-comment/<int:comment_id>/', views.delete_comment, name='delete_comment'),
    path('delete/<int:track_id>/', views.delete_track, name='delete_track'),
    path('play-junction/<int:junction_id>/', views.play_junction, name='play_junction'),  # 追加
    path('delete-junction/<int:junction_id>/', views.delete_junction, name='delete_junction'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('junctify/<str:content_type>/<int:content_id>/', views.junctify_list, name='junctify_list'),
    path('junctify/<str:content_type>/<int:content_id>/create/', views.junctify_create, name='junctify_create'),
    path('impression/<str:content_type>/<int:content_id>/', views.impression, name='impression'),  # 修正
]
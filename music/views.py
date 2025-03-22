import boto3
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.hashers import make_password
from django.contrib.auth.forms import PasswordChangeForm
from django.urls import reverse
from django.http import HttpResponseRedirect, JsonResponse, Http404
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User
from allauth.account.views import LoginView, SignupView, PasswordResetView, PasswordResetDoneView
from .forms import UserChangeForm, EmailChangeForm, ProfileIconForm, ProfileBioForm, TrackForm,JunctionForm,TrackForm,UserChangeForm
from datetime import timedelta  # 追加
from .models import Track, Junction, Profile, Comment, GoodTrack, PlayRecord, ImpressionRecord
from botocore.exceptions import NoCredentialsError, ClientError
import os
import datetime  # 追加
from django.contrib.auth import update_session_auth_hash
from botocore.client import Config
from datetime import datetime
from django.contrib import messages

class CustomLoginView(LoginView):
    template_name = 'registration/login.html'

    def form_invalid(self, form):
        messages.error(self.request, "ログインに失敗しました。ユーザー名またはパスワードが間違っています。")
        return super().form_invalid(form)

class CustomSignupView(SignupView):
    template_name = 'registration/signup.html'

def get_signed_url(file_path):
    if not file_path:
        print("get_signed_url: file_path is empty")
        return None
    print(f"get_signed_url: Generating URL for file_path={file_path}")
    s3_client = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME,
    )
    try:
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                'Key': file_path,
            },
            ExpiresIn=3600
        )
        print(f"get_signed_url: Generated URL={url}")
        return url
    except Exception as e:
        print(f"Error generating signed URL for {file_path}: {e}")
        return None

@login_required
def profile(request):
    tracks = Track.objects.filter(artist=request.user).order_by('-uploaded_at')
    junctions = Junction.objects.filter(collaborator=request.user).order_by('-created_at')

    # 安全に profile にアクセス
    try:
        if request.user.profile and request.user.profile.icon:
            icon_path = request.user.profile.icon.name.strip('/')  # .name を追加
            print(f"User {request.user.id} - Icon path: {icon_path}")
            icon_url = get_signed_url(icon_path)
            print(f"User {request.user.id} - Icon URL: {icon_url}")
        else:
            icon_url = None
            print(f"User {request.user.id} - No icon URL")
    except request.user.profile.RelatedObjectDoesNotExist:
        icon_url = None
        print(f"User {request.user.id} - No profile")

    for track in tracks:
        try:
            if track.artist.profile and track.artist.profile.icon:
                track_icon_path = track.artist.profile.icon.name.strip('/')  # .name を追加
                print(f"Track {track.id} - Icon path: {track_icon_path}")
                track.icon_url = get_signed_url(track_icon_path)
                print(f"Track {track.id} - Icon URL: {track.icon_url}")
            else:
                track.icon_url = None
                print(f"Track {track.id} - No icon URL (artist or profile missing)")
        except track.artist.profile.RelatedObjectDoesNotExist:
            track.icon_url = None
            print(f"Track {track.id} - No profile for artist")

        if track.type == 'audio' and track.audio_file:
            track_audio_path = track.audio_file.name.strip('/')  # .name を追加
            print(f"Track {track.id} - Audio path: {track_audio_path}")
            track.audio_url = get_signed_url(track_audio_path)
            print(f"Track {track.id} - Audio URL: {track.audio_url}")
        elif track.type == 'image' and track.image_file:
            track_image_path = track.image_file.name.strip('/')  # .name を追加
            print(f"Track {track.id} - Image path: {track_image_path}")
            track.image_url = get_signed_url(track_image_path)
            print(f"Track {track.id} - Image URL: {track.image_url}")
        else:
            track.audio_url = None
            track.image_url = None
            print(f"Track {track.id} - No content URL")

    for junction in junctions:
        try:
            if junction.collaborator.profile and junction.collaborator.profile.icon:
                junction_icon_path = junction.collaborator.profile.icon.name.strip('/')  # .name を追加
                print(f"Junction {junction.id} - Icon path: {junction_icon_path}")
                junction.icon_url = get_signed_url(junction_icon_path)
                print(f"Junction {junction.id} - Icon URL: {junction.icon_url}")
            else:
                junction.icon_url = None
                print(f"Junction {junction.id} - No icon URL (collaborator or profile missing)")
        except junction.collaborator.profile.RelatedObjectDoesNotExist:
            junction.icon_url = None
            print(f"Junction {junction.id} - No profile for collaborator")

        if junction.type == 'audio' and junction.audio_file:
            junction_audio_path = junction.audio_file.name.strip('/')  # .name を追加
            print(f"Junction {junction.id} - Audio path: {junction_audio_path}")
            junction.audio_url = get_signed_url(junction_audio_path)
            print(f"Junction {junction.id} - Audio URL: {junction.audio_url}")
        elif junction.type == 'image' and junction.image_file:
            junction_image_path = junction.image_file.name.strip('/')  # .name を追加
            print(f"Junction {junction.id} - Image path: {junction_image_path}")
            junction.image_url = get_signed_url(junction_image_path)
            print(f"Junction {junction.id} - Image URL: {junction.image_url}")
        else:
            junction.audio_url = None
            junction.image_url = None
            print(f"Junction {junction.id} - No content URL")

    return render(request, 'music/profile.html', {
        'tracks': tracks,
        'junctions': junctions,
        'user': request.user,
        'icon_url': icon_url
    })

@login_required
def edit_profile(request):
    user = request.user
    profile = user.profile

    if request.method == 'POST':
        if 'username_update' in request.POST:
            username_form = UserChangeForm(request.POST, instance=user)
            if username_form.is_valid():
                username_form.save()
                return redirect('profile')
        elif 'email_update' in request.POST:
            email_form = EmailChangeForm(request.POST, instance=user)
            if email_form.is_valid():
                email_form.save()
                return redirect('profile')
        elif 'password_update' in request.POST:
            password_form = PasswordChangeForm(user=user, data=request.POST)
            if password_form.is_valid():
                password_form.save()
                update_session_auth_hash(request, user)  # セッションを更新してログアウトを防ぐ
                return redirect('profile')
        elif 'delete_account' in request.POST:
            user.delete()
            return redirect('music_list')
    else:
        username_form = UserChangeForm(instance=user)
        email_form = EmailChangeForm(instance=user)
        password_form = PasswordChangeForm(user=user)

    return render(request, 'music/edit_profile.html', {
        'username_form': username_form,
        'email_form': email_form,
        'password_form': password_form,
        'profile': profile,
    })

@login_required
def upload_music(request):
    if request.method == 'POST':
        print("Received POST request for music upload")
        print(f"POST data: {request.POST}")
        print(f"FILES data: {request.FILES}")
        form = TrackForm(request.POST, request.FILES)
        if form.is_valid():
            print("Track form is valid")
            track = form.save(commit=False)
            track.artist = request.user
            # ファイルアップロード処理
            if track.type == 'audio':
                audio_file = request.FILES.get('audio_file')
                if audio_file:
                    print(f"Audio file received: {audio_file.name}")
                    s3_client = boto3.client(
                        's3',
                        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                        region_name=settings.AWS_S3_REGION_NAME,
                    )
                    try:
                        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                        file_name = f"{timestamp}_{audio_file.name}"
                        s3_path = f"tracks/audio/{file_name}"
                        print(f"Uploading audio file to S3: {s3_path}")
                        print(f"File size: {audio_file.size} bytes")
                        print(f"File content type: {audio_file.content_type}")
                        s3_client.upload_fileobj(
                            audio_file,
                            settings.AWS_STORAGE_BUCKET_NAME,
                            s3_path,
                            ExtraArgs={'ContentType': audio_file.content_type}  # ACL を削除
                        )
                        print(f"Audio file successfully uploaded to S3: {s3_path}")
                        # アップロード後にファイルが存在するか確認
                        try:
                            s3_client.head_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=s3_path)
                            print(f"Confirmed: File exists in S3 at {s3_path}")
                        except Exception as e:
                            print(f"Error: File does not exist in S3 after upload: {e}")
                        track.audio_file = s3_path
                        track.image_file = ''
                        print(f"Track audio file saved: {track.audio_file}")
                    except Exception as e:
                        print(f"Error uploading audio file to S3: {e}")
                        print(f"S3 Bucket: {settings.AWS_STORAGE_BUCKET_NAME}")
                        print(f"AWS Access Key ID: {settings.AWS_ACCESS_KEY_ID}")
                        print(f"AWS Region: {settings.AWS_S3_REGION_NAME}")
                        return render(request, 'music/upload.html', {
                            'form': form,
                            'title': 'Upload Content',
                            'header': 'Upload Content',
                            'error': 'Failed to upload audio file'
                        })
                else:
                    print("No audio file provided - check if file was selected in the form")
            elif track.type == 'image':
                image_file = request.FILES.get('image_file')
                if image_file:
                    print(f"Image file received: {image_file.name}")
                    s3_client = boto3.client(
                        's3',
                        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                        region_name=settings.AWS_S3_REGION_NAME,
                    )
                    try:
                        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                        file_name = f"{timestamp}_{image_file.name}"
                        s3_path = f"tracks/images/{file_name}"
                        print(f"Uploading image file to S3: {s3_path}")
                        print(f"File size: {image_file.size} bytes")
                        print(f"File content type: {image_file.content_type}")
                        s3_client.upload_fileobj(
                            image_file,
                            settings.AWS_STORAGE_BUCKET_NAME,
                            s3_path,
                            ExtraArgs={'ContentType': image_file.content_type}  # ACL を削除
                        )
                        print(f"Image file successfully uploaded to S3: {s3_path}")
                        # アップロード後にファイルが存在するか確認
                        try:
                            s3_client.head_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=s3_path)
                            print(f"Confirmed: File exists in S3 at {s3_path}")
                        except Exception as e:
                            print(f"Error: File does not exist in S3 after upload: {e}")
                        track.image_file = s3_path
                        track.audio_file = ''
                        print(f"Track image file saved: {track.image_file}")
                    except Exception as e:
                        print(f"Error uploading image file to S3: {e}")
                        print(f"S3 Bucket: {settings.AWS_STORAGE_BUCKET_NAME}")
                        print(f"AWS Access Key ID: {settings.AWS_ACCESS_KEY_ID}")
                        print(f"AWS Region: {settings.AWS_S3_REGION_NAME}")
                        return render(request, 'music/upload.html', {
                            'form': form,
                            'title': 'Upload Content',
                            'header': 'Upload Content',
                            'error': 'Failed to upload image file'
                        })
                else:
                    print("No image file provided - check if file was selected in the form")
            track.save()
            print(f"Track saved: {track.id} - {track.title} by {track.artist.username}")
            print(f"Track audio file: {track.audio_file}")
            print(f"Track image file: {track.image_file}")
            return redirect('music_list')
        else:
            print("Track form errors:", form.errors)
    else:
        form = TrackForm()
    return render(request, 'music/upload.html', {
        'form': form,
        'title': 'Upload Content',
        'header': 'Upload Content',
    })

def music_list(request):
    type_filter = request.GET.get('type')

    # Track と Junction を取得
    tracks = Track.objects.all()
    junctions = Junction.objects.all()

    # Track と Junction を統合してリスト化
    items = []
    for track in tracks:
        # 動的に URL を設定
        track_audio_url = None
        track_image_url = None
        track_icon_url = None
        if track.type == 'audio' and track.audio_file:
            track_audio_path = track.audio_file.strip('/')
            print(f"Track {track.id} - Audio path: {track_audio_path}")
            track_audio_url = get_signed_url(track_audio_path)
            print(f"Track {track.id} - Audio URL: {track_audio_url}")
        elif track.type == 'image' and track.image_file:
            track_image_path = track.image_file.strip('/')
            print(f"Track {track.id} - Image path: {track_image_path}")
            track_image_url = get_signed_url(track_image_path)
            print(f"Track {track.id} - Image URL: {track_image_url}")
        if track.artist:
            print(f"Track {track.id} - Artist: {track.artist.username}")
            if hasattr(track.artist, 'profile'):
                print(f"Track {track.id} - Has profile: {track.artist.profile}")
                if track.artist.profile and track.artist.profile.icon:
                    track_icon_path = track.artist.profile.icon.strip('/')
                    print(f"Track {track.id} - Icon path: {track_icon_path}")
                    track_icon_url = get_signed_url(track_icon_path)
                    if not track_icon_url:
                        print(f"Track {track.id} - Failed to generate icon URL")
                    print(f"Track {track.id} - Icon URL: {track_icon_url}")
                else:
                    print(f"Track {track.id} - No icon in profile")
            else:
                print(f"Track {track.id} - No profile for artist")
        else:
            print(f"Track {track.id} - No artist")

        items.append({
            'type': 'track',
            'obj': track,
            'timestamp': track.uploaded_at,
            'audio_url': track_audio_url,
            'image_url': track_image_url,
            'icon_url': track_icon_url,
        })

    for junction in junctions:
        # 動的に URL を設定
        junction_audio_url = None
        junction_image_url = None
        junction_icon_url = None
        if junction.type == 'audio' and junction.audio_file:
            junction_audio_path = junction.audio_file.strip('/')
            print(f"Junction {junction.id} - Audio path: {junction_audio_path}")
            junction_audio_url = get_signed_url(junction_audio_path)
            print(f"Junction {junction.id} - Audio URL: {junction_audio_url}")
        elif junction.type == 'image' and junction.image_file:
            junction_image_path = junction.image_file.strip('/')
            print(f"Junction {junction.id} - Image path: {junction_image_path}")
            junction_image_url = get_signed_url(junction_image_path)
            print(f"Junction {junction.id} - Image URL: {junction_image_url}")
        if junction.collaborator:
            print(f"Junction {junction.id} - Collaborator: {junction.collaborator.username}")
            if hasattr(junction.collaborator, 'profile'):
                print(f"Junction {junction.id} - Has profile: {junction.collaborator.profile}")
                if junction.collaborator.profile and junction.collaborator.profile.icon:
                    junction_icon_path = junction.collaborator.profile.icon.strip('/')
                    print(f"Junction {junction.id} - Icon path: {junction_icon_path}")
                    junction_icon_url = get_signed_url(junction_icon_path)
                    if not junction_icon_url:
                        print(f"Junction {junction.id} - Failed to generate icon URL")
                    print(f"Junction {junction.id} - Icon URL: {junction_icon_url}")
                else:
                    print(f"Junction {junction.id} - No icon in profile")
            else:
                print(f"Junction {junction.id} - No profile for collaborator")
        else:
            print(f"Junction {junction.id} - No collaborator")

        items.append({
            'type': 'junction',
            'obj': junction,
            'timestamp': junction.created_at,
            'audio_url': junction_audio_url,
            'image_url': junction_image_url,
            'icon_url': junction_icon_url,
        })

    # 時系列順（新しい順）に並べ替え
    items.sort(key=lambda x: x['timestamp'], reverse=True)

    # フィルタリングを適用
    if type_filter:
        items = [item for item in items if item['obj'].type == type_filter]

    return render(request, 'music/list.html', {
        'items': items,
        'type_filter': type_filter,
    })

def user_profile(request, username):
    user = get_object_or_404(User, username=username)
    tracks = Track.objects.filter(artist=user).order_by('-uploaded_at')
    junctions = Junction.objects.filter(collaborator=user).order_by('-created_at')

    # プロフィールが存在しない場合の処理
    try:
        profile = user.profile
        if profile.icon:
            icon_path = profile.icon.strip('/')
            print(f"User {user.username} - Icon path: {icon_path}")
            profile.icon_url = get_signed_url(icon_path)
            if not profile.icon_url:
                print(f"User {user.username} - Failed to generate icon URL")
            print(f"User {user.username} - Icon URL: {profile.icon_url}")
        else:
            profile.icon_url = None
            print(f"User {user.username} - No icon set in profile")
    except Profile.DoesNotExist:
        print(f"User {user.username} - Profile does not exist")
        user.profile = None

    for track in tracks:
        if track.type == 'audio' and track.audio_file:
            track_audio_path = track.audio_file.strip('/')
            print(f"Track {track.id} - Audio path: {track_audio_path}")
            track.audio_url = get_signed_url(track_audio_path)
            print(f"Track {track.id} - Audio URL: {track.audio_url}")
        elif track.type == 'image' and track.image_file:
            track_image_path = track.image_file.strip('/')
            print(f"Track {track.id} - Image path: {track_image_path}")
            track.image_url = get_signed_url(track_image_path)
            print(f"Track {track.id} - Image URL: {track.image_url}")
        if track.artist and hasattr(track.artist, 'profile') and track.artist.profile and track.artist.profile.icon:
            track_icon_path = track.artist.profile.icon.strip('/')
            print(f"Track {track.id} - Icon path: {track_icon_path}")
            track.icon_url = get_signed_url(track_icon_path)
            if not track.icon_url:
                print(f"Track {track.id} - Failed to generate icon URL")
            print(f"Track {track.id} - Icon URL: {track.icon_url}")
        else:
            track.icon_url = None
            print(f"Track {track.id} - No icon URL (artist or profile missing)")

    for junction in junctions:
        if junction.type == 'audio' and junction.audio_file:
            junction_audio_path = junction.audio_file.strip('/')
            print(f"Junction {junction.id} - Audio path: {junction_audio_path}")
            junction.audio_url = get_signed_url(junction_audio_path)
            print(f"Junction {junction.id} - Audio URL: {junction.audio_url}")
        elif junction.type == 'image' and junction.image_file:
            junction_image_path = junction.image_file.strip('/')
            print(f"Junction {junction.id} - Image path: {junction_image_path}")
            junction.image_url = get_signed_url(junction_image_path)
            print(f"Junction {junction.id} - Image URL: {junction.image_url}")
        if junction.collaborator and hasattr(junction.collaborator, 'profile') and junction.collaborator.profile and junction.collaborator.profile.icon:
            junction_icon_path = junction.collaborator.profile.icon.strip('/')
            print(f"Junction {junction.id} - Icon path: {junction_icon_path}")
            junction.icon_url = get_signed_url(junction_icon_path)
            if not junction.icon_url:
                print(f"Junction {junction.id} - Failed to generate icon URL")
            print(f"Junction {junction.id} - Icon URL: {junction.icon_url}")
        else:
            junction.icon_url = None
            print(f"Junction {junction.id} - No icon URL (collaborator or profile missing)")

    return render(request, 'music/user_profile.html', {
        'user': user,
        'tracks': tracks,
        'junctions': junctions,
    })

@login_required
def logout(request):
    auth_logout(request)
    return redirect('music_list')

@login_required
def delete_track(request, track_id):
    track = get_object_or_404(Track, id=track_id, artist=request.user)
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
        file_key = track.audio_file.replace(f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/", "")
        s3_client.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=file_key)
        track.delete()
        return JsonResponse({'status': 'deleted'}, status=200)
    except Exception as e:
        print(f"Error in delete_track: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@login_required
def good_track(request, content_type, content_id):
    if content_type == 'track':
        content = get_object_or_404(Track, id=content_id)
        junction = None
    elif content_type == 'junction':
        content = None
        junction = get_object_or_404(Junction, id=content_id)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid content type'}, status=400)

    try:
        print(f"Good request for {content_type} {content_id} by user {request.user.username}")
        good, created = GoodTrack.objects.get_or_create(
            user=request.user,
            track=content,
            junction=junction
        )
        if not created:
            good.delete()
            good_count = GoodTrack.objects.filter(track=content, junction=junction).count()
            print(f"Good removed, new count: {good_count}")
            return JsonResponse({'status': 'removed', 'good_count': good_count}, status=200)
        good_count = GoodTrack.objects.filter(track=content, junction=junction).count()
        print(f"Good added, new count: {good_count}")
        return JsonResponse({'status': 'added', 'good_count': good_count}, status=200)
    except Exception as e:
        print(f"Error in good_track: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@login_required
def comment_track(request, content_type, content_id):
    if content_type == 'track':
        content = get_object_or_404(Track, id=content_id)
        junction = None
    elif content_type == 'junction':
        content = None
        junction = get_object_or_404(Junction, id=content_id)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid content type'}, status=400)

    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

    text = request.POST.get('text')
    if not text:
        return JsonResponse({'status': 'error', 'message': 'Comment text is required'}, status=400)

    try:
        comment = Comment.objects.create(
            user=request.user,
            track=content,
            junction=junction,
            text=text
        )
        print(f"Comment created: {comment.id} for {content_type} {content_id}")
        return JsonResponse({'status': 'success'}, status=200)
    except Exception as e:
        print(f"Error in comment_track: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, user=request.user)
    try:
        comment.delete()
        print(f"Comment {comment_id} deleted")
        return JsonResponse({'status': 'deleted'}, status=200)
    except Exception as e:
        print(f"Error in delete_comment: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

class CustomPasswordResetView(PasswordResetView):
    template_name = 'registration/password_reset.html'

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'registration/password_reset_done.html'

@login_required
def junctify_list(request, content_type, content_id):
    if content_type == 'track':
        content = get_object_or_404(Track, id=content_id)
        # 大元の Track に関連するすべての Junction を取得
        junctions = Junction.objects.filter(track=content).order_by('-created_at')
    elif content_type == 'junction':
        content = get_object_or_404(Junction, id=content_id)
        # 大元の Track に関連するすべての Junction を取得
        junctions = Junction.objects.filter(track=content.track).order_by('-created_at')
    else:
        return redirect('music_list')

    # Junction の URL を設定
    for junction in junctions:
        if junction.collaborator.profile and junction.collaborator.profile.icon:
            junction_icon_path = junction.collaborator.profile.icon.strip('/')
            print(f"Junction {junction.id} - Icon path: {junction_icon_path}")
            junction.icon_url = get_signed_url(junction_icon_path)
            print(f"Junction {junction.id} - Icon URL: {junction.icon_url}")
        else:
            junction.icon_url = None
            print(f"Junction {junction.id} - No icon URL (collaborator or profile missing)")

        if junction.type == 'audio' and junction.audio_file:
            junction_audio_path = junction.audio_file.strip('/')
            print(f"Junction {junction.id} - Audio path: {junction_audio_path}")
            junction.audio_url = get_signed_url(junction_audio_path)
            print(f"Junction {junction.id} - Audio URL: {junction.audio_url}")
        elif junction.type == 'image' and junction.image_file:
            junction_image_path = junction.image_file.strip('/')
            print(f"Junction {junction.id} - Image path: {junction_image_path}")
            junction.image_url = get_signed_url(junction_image_path)
            print(f"Junction {junction.id} - Image URL: {junction.image_url}")
        else:
            junction.audio_url = None
            junction.image_url = None
            print(f"Junction {junction.id} - No content URL")

    # 大元の Track の URL を設定
    if content_type == 'junction':
        track = content.track
    else:
        track = content

    if track.artist.profile and track.artist.profile.icon:
        track_icon_path = track.artist.profile.icon.strip('/')
        print(f"Track {track.id} - Icon path: {track_icon_path}")
        track.icon_url = get_signed_url(track_icon_path)
        print(f"Track {track.id} - Icon URL: {track.icon_url}")
    else:
        track.icon_url = None
        print(f"Track {track.id} - No icon URL (artist or profile missing)")

    if track.type == 'audio' and track.audio_file:
        track_audio_path = track.audio_file.strip('/')
        print(f"Track {track.id} - Audio path: {track_audio_path}")
        track.audio_url = get_signed_url(track_audio_path)
        print(f"Track {track.id} - Audio URL: {track.audio_url}")
    elif track.type == 'image' and track.image_file:
        track_image_path = track.image_file.strip('/')
        print(f"Track {track.id} - Image path: {track_image_path}")
        track.image_url = get_signed_url(track_image_path)
        print(f"Track {track.id} - Image URL: {track.image_url}")
    else:
        track.audio_url = None
        track.image_url = None
        print(f"Track {track.id} - No content URL")

    # デバッグログを追加
    print(f"Track {track.id} - Title: {track.title}")
    print(f"Track {track.id} - Artist: {track.artist.username if track.artist else 'None'}")
    print(f"Track {track.id} - Uploaded At: {track.uploaded_at}")
    print(f"Track {track.id} - Type: {track.type}")
    print(f"Track {track.id} - Audio File: {track.audio_file}")
    print(f"Track {track.id} - Image File: {track.image_file}")

    return render(request, 'music/junctify_list.html', {
        'content': content,
        'content_type': content_type,
        'junctions': junctions,
        'user': request.user,
        'track': track  # 明示的に track を渡す
    })

@login_required
def junctify_create(request, content_type, content_id):
    if content_type == 'track':
        content = get_object_or_404(Track, id=content_id)
    elif content_type == 'junction':
        content = get_object_or_404(Junction, id=content_id)
    else:
        return redirect('music_list')

    if request.method == 'POST':
        print("Received POST request for junctify_create")
        print(f"POST data: {request.POST}")
        print(f"FILES data: {request.FILES}")
        form = JunctionForm(request.POST, request.FILES)
        if form.is_valid():
            print("Junction form is valid")
            junction = form.save(commit=False)
            junction.collaborator = request.user
            # type を明示的に設定
            junction_type = request.POST.get('type')
            print(f"Junction type from form: {junction_type}")
            if junction_type not in ['audio', 'image']:
                print("Invalid junction type, defaulting to 'audio'")
                junction_type = 'audio'
            junction.type = junction_type
            print(f"Junction type set to: {junction.type}")

            # 親トラックと親ジャンクションを設定
            if content_type == 'track':
                junction.track = content
                junction.parent_junction = None
                print(f"Creating Junction for Track {content.id}")
            else:
                junction.track = content.track  # 大元の Track を保持
                junction.parent_junction = content  # 親 Junction を設定
                print(f"Creating Junction for Junction {content.id}, parent Track {content.track.id}")

            # ファイルアップロード処理
            if junction.type == 'audio':
                audio_file = request.FILES.get('audio_file')
                if audio_file:
                    print(f"Audio file received: {audio_file.name}")
                    s3_client = boto3.client(
                        's3',
                        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                        region_name=settings.AWS_S3_REGION_NAME,
                    )
                    try:
                        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                        file_name = f"{timestamp}_{audio_file.name}"
                        s3_path = f"junctions/audio/{file_name}"
                        print(f"Uploading audio file to S3: {s3_path}")
                        print(f"File size: {audio_file.size} bytes")
                        print(f"File content type: {audio_file.content_type}")
                        s3_client.upload_fileobj(
                            audio_file,
                            settings.AWS_STORAGE_BUCKET_NAME,
                            s3_path,
                            ExtraArgs={'ContentType': audio_file.content_type}
                        )
                        print(f"Audio file successfully uploaded to S3: {s3_path}")
                        # アップロード後にファイルが存在するか確認
                        try:
                            s3_client.head_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=s3_path)
                            print(f"Confirmed: File exists in S3 at {s3_path}")
                        except Exception as e:
                            print(f"Error: File does not exist in S3 after upload: {e}")
                        junction.audio_file = s3_path
                        junction.image_file = ''
                        print(f"Junction audio file saved: {junction.audio_file}")
                    except Exception as e:
                        print(f"Error uploading audio file to S3: {e}")
                        print(f"S3 Bucket: {settings.AWS_STORAGE_BUCKET_NAME}")
                        print(f"AWS Access Key ID: {settings.AWS_ACCESS_KEY_ID}")
                        print(f"AWS Region: {settings.AWS_S3_REGION_NAME}")
                        return render(request, 'music/junctify_create.html', {
                            'form': form,
                            'content': content,
                            'content_type': content_type,
                            'error': 'Failed to upload audio file'
                        })
                else:
                    print("No audio file provided - check if file was selected in the form")
            elif junction.type == 'image':
                image_file = request.FILES.get('image_file')
                if image_file:
                    print(f"Image file received: {image_file.name}")
                    s3_client = boto3.client(
                        's3',
                        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                        region_name=settings.AWS_S3_REGION_NAME,
                    )
                    try:
                        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                        file_name = f"{timestamp}_{image_file.name}"
                        s3_path = f"junctions/images/{file_name}"
                        print(f"Uploading image file to S3: {s3_path}")
                        print(f"File size: {image_file.size} bytes")
                        print(f"File content type: {image_file.content_type}")
                        s3_client.upload_fileobj(
                            image_file,
                            settings.AWS_STORAGE_BUCKET_NAME,
                            s3_path,
                            ExtraArgs={'ContentType': image_file.content_type}
                        )
                        print(f"Image file successfully uploaded to S3: {s3_path}")
                        # アップロード後にファイルが存在するか確認
                        try:
                            s3_client.head_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=s3_path)
                            print(f"Confirmed: File exists in S3 at {s3_path}")
                        except Exception as e:
                            print(f"Error: File does not exist in S3 after upload: {e}")
                        junction.image_file = s3_path
                        junction.audio_file = ''
                        print(f"Junction image file saved: {junction.image_file}")
                    except Exception as e:
                        print(f"Error uploading image file to S3: {e}")
                        print(f"S3 Bucket: {settings.AWS_STORAGE_BUCKET_NAME}")
                        print(f"AWS Access Key ID: {settings.AWS_ACCESS_KEY_ID}")
                        print(f"AWS Region: {settings.AWS_S3_REGION_NAME}")
                        return render(request, 'music/junctify_create.html', {
                            'form': form,
                            'content': content,
                            'content_type': content_type,
                            'error': 'Failed to upload image file'
                        })
                else:
                    print("No image file provided - check if file was selected in the form")
            junction.save()
            print(f"Junction saved: {junction.id} - {junction.title} by {junction.collaborator.username} (Type: {junction.type})")
            print(f"Junction audio file: {junction.audio_file}")
            print(f"Junction image file: {junction.image_file}")
            return redirect('music_list')
        else:
            print("Junction form errors:", form.errors)
    else:
        form = JunctionForm()
    return render(request, 'music/junctify_create.html', {
        'form': form,
        'content': content,
        'content_type': content_type,
    })

@login_required
def delete_junction(request, junction_id):
    if request.method == 'POST':
        try:
            junction = Junction.objects.get(id=junction_id)
            if junction.collaborator != request.user:
                return JsonResponse({'status': 'error', 'message': 'You are not authorized to delete this junction'}, status=403)
            junction.delete()
            return JsonResponse({'status': 'deleted'})
        except Junction.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Junction not found'}, status=404)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

from django.contrib.contenttypes.models import ContentType
from .models import Comment

@login_required
def add_comment(request, content_type, content_id):
    if request.method == 'POST':
        text = request.POST.get('text')
        if not text:
            return JsonResponse({'status': 'error', 'message': 'Comment text is required'}, status=400)

        try:
            # ContentType を取得
            if content_type == 'track':
                model_class = Track
            elif content_type == 'junction':
                model_class = Junction
            else:
                return JsonResponse({'status': 'error', 'message': 'Invalid content type'}, status=400)

            content_type_obj = ContentType.objects.get_for_model(model_class)
            content_object = model_class.objects.get(id=content_id)

            # コメントを作成
            comment = Comment.objects.create(
                user=request.user,
                content_type=content_type_obj,
                object_id=content_id,
                text=text
            )
            return JsonResponse({'status': 'success'})
        except (ContentType.DoesNotExist, model_class.DoesNotExist):
            return JsonResponse({'status': 'error', 'message': 'Content not found'}, status=404)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

@login_required
def play_track(request, track_id):
    if request.method == 'POST':
        track = get_object_or_404(Track, id=track_id)

        # 1日以内に同じユーザーによる再生記録があるか確認
        one_day_ago = timezone.now() - timedelta(days=1)
        existing_play = PlayRecord.objects.filter(
            user=request.user,
            content_type=ContentType.objects.get_for_model(Track),
            object_id=track_id,
            played_at__gte=one_day_ago
        ).exists()

        if not existing_play:
            # 再生記録がない場合、カウントを増やして記録を保存
            track.play_count += 1
            track.save()
            PlayRecord.objects.create(
                user=request.user,
                content_type=ContentType.objects.get_for_model(Track),
                object_id=track_id
            )
            print(f"Track {track_id} play count updated: {track.play_count}")

        return JsonResponse({'status': 'success', 'play_count': track.play_count})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

@login_required
def play_junction(request, junction_id):
    if request.method == 'POST':
        junction = get_object_or_404(Junction, id=junction_id)

        # 1日以内に同じユーザーによる再生記録があるか確認
        one_day_ago = timezone.now() - timedelta(days=1)
        existing_play = PlayRecord.objects.filter(
            user=request.user,
            content_type=ContentType.objects.get_for_model(Junction),
            object_id=junction_id,
            played_at__gte=one_day_ago
        ).exists()

        if not existing_play:
            # 再生記録がない場合、カウントを増やして記録を保存
            junction.play_count += 1
            junction.save()
            PlayRecord.objects.create(
                user=request.user,
                content_type=ContentType.objects.get_for_model(Junction),
                object_id=junction_id
            )
            print(f"Junction {junction_id} play count updated: {junction.play_count}")

        return JsonResponse({'status': 'success', 'play_count': junction.play_count})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

@login_required
def impression(request, content_type, content_id):
    if request.method == 'POST':
        try:
            if content_type == 'track':
                content = Track.objects.get(id=content_id)
            elif content_type == 'junction':
                content = Junction.objects.get(id=content_id)
            else:
                return JsonResponse({'status': 'error', 'message': 'Invalid content type'}, status=400)

            # 1日以内に同じユーザーによるインプレッション記録があるか確認
            one_day_ago = timezone.now() - timedelta(days=1)
            existing_impression = ImpressionRecord.objects.filter(
                user=request.user,
                content_type=ContentType.objects.get_for_model(content),
                object_id=content_id,
                impressed_at__gte=one_day_ago
            ).exists()

            if not existing_impression:
                # インプレッション記録がない場合、カウントを増やして記録を保存
                content.impression_count += 1
                content.save()
                ImpressionRecord.objects.create(
                    user=request.user,
                    content_type=ContentType.objects.get_for_model(content),
                    object_id=content_id
                )
                print(f"{content_type.capitalize()} {content_id} impression count updated: {content.impression_count}")

            return JsonResponse({'status': 'success', 'impression_count': content.impression_count})
        except (Track.DoesNotExist, Junction.DoesNotExist):
            return JsonResponse({'status': 'error', 'message': f'{content_type.capitalize()} not found'}, status=404)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)
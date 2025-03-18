import boto3
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.hashers import make_password
from django.urls import reverse
from django.http import HttpResponseRedirect, JsonResponse
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User
from allauth.account.views import LoginView, SignupView, PasswordResetView, PasswordResetDoneView
from .forms import UsernameChangeForm, EmailChangeForm, PasswordChangeForm, IconForm, BioForm, MusicPostForm
from .models import Track, Profile, GoodTrack, Comment, PlayHistory
from botocore.exceptions import NoCredentialsError, ClientError

class CustomLoginView(LoginView):
    template_name = 'registration/login.html'

class CustomSignupView(SignupView):
    template_name = 'registration/signup.html'

# 署名付きURL生成関数
def get_signed_url(file_name):
    if not file_name:
        return None
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME, 'Key': file_name.replace(f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/", "")},
            ExpiresIn=3600
        )
        print(f"Generated signed URL for {file_name}: {url}")
        return url
    except (NoCredentialsError, ClientError) as e:
        print(f"Error generating signed URL for {file_name}: {e}")
        return None

@login_required
def profile(request):
    user = request.user
    profile, created = Profile.objects.get_or_create(user=user)
    
    if request.method == 'POST':
        if 'icon_update' in request.POST:
            icon_form = IconForm(request.POST, request.FILES, instance=profile)
            if icon_form.is_valid():
                s3_client = boto3.client(
                    's3',
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                    region_name=settings.AWS_S3_REGION_NAME
                )
                if 'icon' in request.FILES:
                    old_icon = profile.icon if profile.icon else None
                    if old_icon:
                        try:
                            old_icon_key = old_icon.replace(f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/", "")
                            s3_client.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=old_icon_key)
                            print(f"Deleted old icon: {old_icon_key}")
                        except ClientError as e:
                            print(f"Error deleting old icon: {e}")
                    file_name = request.FILES['icon'].name
                    file_key = f"icons/{file_name}"
                    try:
                        s3_client.upload_fileobj(
                            request.FILES['icon'],
                            settings.AWS_STORAGE_BUCKET_NAME,
                            file_key
                        )
                        profile.icon = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{file_key}"
                        print(f"Uploaded new icon to S3: {profile.icon}")
                    except ClientError as e:
                        print(f"Error uploading icon to S3: {e}")
                        return JsonResponse({'status': 'error', 'message': f"Failed to upload icon: {str(e)}"}, status=400)
                profile.save()
                profile.refresh_from_db()
                print(f"After saving: Icon URL: {profile.icon}")
                return redirect('profile')
            else:
                errors = icon_form.errors.as_json()
                print(f"Icon form errors: {errors}")
                return JsonResponse({'status': 'error', 'message': errors}, status=400)
        
        elif 'bio_update' in request.POST:
            bio_form = BioForm(request.POST, instance=profile)
            if bio_form.is_valid():
                profile.bio = bio_form.cleaned_data['bio']
                profile.save()
                profile.refresh_from_db()
                print(f"After saving: Bio: {profile.bio}")
                return redirect('profile')
            else:
                errors = bio_form.errors.as_json()
                print(f"Bio form errors: {errors}")
                return JsonResponse({'status': 'error', 'message': errors}, status=400)
    else:
        icon_form = IconForm(instance=profile)
        bio_form = BioForm(instance=profile)

    tracks = Track.objects.filter(artist=user).order_by('-uploaded_at')
    if not tracks.exists():
        print(f"No tracks found for user {user.username}, checking database...")
        all_tracks = Track.objects.all()
        for track in all_tracks:
            print(f"Track: {track.id}, Title: {track.title}, Artist: {track.artist.username if track.artist else 'None'}")

    # アイコンURLを生成
    icon_url = get_signed_url(profile.icon) if profile.icon else None
    print(f"Generated Icon URL for user {user.username}: {icon_url}")

    # 各トラックの署名付きURLを生成
    for track in tracks:
        track.audio_url = get_signed_url(track.audio_file.replace(f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/", "")) if track.audio_file else None
        print(f"Track {track.id} in profile - Audio URL: {track.audio_url}")
    print(f"Tracks for user {user.username}: {list(tracks)}")

    return render(request, 'music/profile.html', {
        'user': user,
        'tracks': tracks,
        'icon_form': icon_form,
        'bio_form': bio_form,
        'icon_url': icon_url,
    })

@login_required
def edit_profile(request):
    user = request.user
    if request.method == 'POST':
        if 'username_update' in request.POST:
            username_form = UsernameChangeForm(request.POST)
            username_form.request = request
            if username_form.is_valid():
                new_username = username_form.cleaned_data['new_username']
                user.username = new_username
                user.save()
                return redirect('profile')
        elif 'email_update' in request.POST:
            email_form = EmailChangeForm(request.POST)
            email_form.request = request
            if email_form.is_valid():
                new_email = email_form.cleaned_data['new_email']
                user.email = new_email
                user.save()
                return redirect('profile')
        elif 'password_update' in request.POST:
            password_form = PasswordChangeForm(user, request.POST)
            if password_form.is_valid():
                new_password = password_form.cleaned_data['new_password1']
                user.password = make_password(new_password)
                user.save()
                return redirect('profile')
            else:
                print(f"Password form errors: {password_form.errors}")
        elif 'delete_account' in request.POST:
            password_form = PasswordChangeForm(user, request.POST)
            if password_form.is_valid() and password_form.cleaned_data['current_password']:
                if user.check_password(password_form.cleaned_data['current_password']):
                    auth_logout(request)
                    user.delete()
                    return redirect('/')
                else:
                    password_form.add_error('current_password', 'Incorrect password.')
    else:
        username_form = UsernameChangeForm()
        email_form = EmailChangeForm()
        password_form = PasswordChangeForm(user)

    return render(request, 'music/edit_profile.html', {
        'username_form': username_form,
        'email_form': email_form,
        'password_form': password_form,
    })

@login_required
def upload_music(request):
    if request.method == 'POST':
        form = MusicPostForm(request.POST, request.FILES)
        if form.is_valid():
            track = form.save(commit=False)
            track.artist = request.user
            audio_file = request.FILES['audio_file']
            file_name = audio_file.name
            print(f"Before save - Original file name: {file_name}")
            s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME
            )
            file_key = f"music/{file_name}"
            try:
                s3_client.upload_fileobj(
                    audio_file,
                    settings.AWS_STORAGE_BUCKET_NAME,
                    file_key
                )
                print(f"Uploaded to S3: {file_key}")
                audio_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{file_key}"
                track.audio_file = audio_url
                track.save()
                print(f"Uploaded track: {track.title}, Artist: {track.artist.username}, Audio URL: {audio_url}, Saved Track: {Track.objects.get(id=track.id)}")
                signed_url = get_signed_url(file_key)
                print(f"Generated signed URL for audio: {signed_url}")
                return redirect('music_list')
            except ClientError as e:
                print(f"Error uploading to S3: {e}")
                return JsonResponse({'status': 'error', 'message': f"Failed to upload music: {str(e)}"}, status=400)
        else:
            errors = form.errors.as_json()
            print(f"Form errors: {errors}")
            return JsonResponse({'status': 'error', 'message': errors}, status=400)
    else:
        form = MusicPostForm()
    return render(request, 'music/upload.html', {'form': form})

def music_list(request):
    tracks = Track.objects.all()
    for track in tracks:
        track.audio_url = get_signed_url(track.audio_file.replace(f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/", "")) if track.audio_file else None
        print(f"Track {track.id} - Audio URL: {track.audio_url}")
        if track.artist and hasattr(track.artist, 'profile') and track.artist.profile.icon:
            track.icon_url = get_signed_url(track.artist.profile.icon.replace(f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/", "")) if track.artist.profile.icon else None
            print(f"Track {track.id} - Icon URL: {track.icon_url}")
        else:
            track.icon_url = None
            print(f"Track {track.id} - No icon URL (artist or profile missing)")
    return render(request, 'music/list.html', {'tracks': tracks})

def user_profile(request, username):
    user = get_object_or_404(User, username=username)
    profile, created = Profile.objects.get_or_create(user=user)
    
    icon_url = get_signed_url(profile.icon.replace(f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/", "")) if profile.icon else None
    print(f"Generated Icon URL for {username}: {icon_url}")

    tracks = Track.objects.filter(artist=user).order_by('-uploaded_at')
    for track in tracks:
        track.audio_url = get_signed_url(track.audio_file.replace(f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/", "")) if track.audio_file else None
        print(f"Track {track.id} in profile - Audio URL: {track.audio_url}")
        track.icon_url = get_signed_url(track.artist.profile.icon.replace(f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/", "")) if track.artist.profile.icon else None
        print(f"Track {track.id} in profile - Icon URL: {track.icon_url}")
        track.good_count = track.goodtrack_set.count()
        track.comments = track.comment_set.all()

    print(f"Viewing profile of {username}, found {tracks.count()} tracks")
    return render(request, 'music/user_profile.html', {
        'profile_user': user,
        'tracks': tracks,
        'icon_url': icon_url,
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
def good_track(request, track_id):
    track = get_object_or_404(Track, id=track_id)
    try:
        print(f"Good request for track {track_id} by user {request.user.username}")
        good, created = GoodTrack.objects.get_or_create(user=request.user, track=track)
        if not created:
            good.delete()
            good_count = track.goodtrack_set.count()
            print(f"Good removed, new count: {good_count}")
            return JsonResponse({'status': 'removed', 'good_count': good_count}, status=200)
        good_count = track.goodtrack_set.count()
        print(f"Good added, new count: {good_count}")
        return JsonResponse({'status': 'added', 'good_count': good_count}, status=200)
    except Exception as e:
        print(f"Error in good_track: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

def play_track(request, track_id):
    track = get_object_or_404(Track, id=track_id)
    today = timezone.now().date()

    try:
        print(f"Play request for track {track_id}")
        if request.user.is_authenticated:
            user = request.user
            anonymous_id = None
            print(f"Checking play history for user: {user.id}, track: {track.id}, date: {today}")
            play_history_exists = PlayHistory.objects.filter(
                user=user,
                anonymous_id__isnull=True,
                track=track,
                played_at=today
            ).exists()
        else:
            if not request.session.session_key:
                request.session.create()
            anonymous_id = request.session.session_key
            print(f"Checking play history for anonymous user: {anonymous_id}, track: {track.id}, date: {today}")
            play_history_exists = PlayHistory.objects.filter(
                user__isnull=True,
                anonymous_id=anonymous_id,
                track=track,
                played_at=today
            ).exists()
            user = None

        if not play_history_exists:
            print(f"Creating play history for {'user ' + str(user.id) if user else 'anonymous user ' + anonymous_id}, track: {track.id}")
            PlayHistory.objects.create(user=user, anonymous_id=anonymous_id, track=track, played_at=today)
            track.play_count += 1
            track.save()
            print(f"Play count updated to: {track.play_count}")
        else:
            print(f"Play history already exists for {'user ' + str(user.id) if user else 'anonymous user ' + anonymous_id}, track: {track.id}, date: {today}")

        return JsonResponse({'play_count': track.play_count}, status=200)
    except Exception as e:
        print(f"Error in play_track: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@login_required
def comment_track(request, track_id):
    track = get_object_or_404(Track, id=track_id)
    try:
        text = request.POST.get('text')
        if text:
            comment = Comment.objects.create(user=request.user, track=track, text=text)
            return JsonResponse({'status': 'success', 'comment_id': comment.id}, status=200)
        return JsonResponse({'status': 'error', 'message': 'No text provided'}, status=400)
    except Exception as e:
        print(f"Error in comment_track: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, user=request.user)
    try:
        comment.delete()
        return JsonResponse({'status': 'deleted'}, status=200)
    except Exception as e:
        print(f"Error in delete_comment: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

class CustomPasswordResetView(PasswordResetView):
    template_name = 'registration/password_reset.html'

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'registration/password_reset_done.html'
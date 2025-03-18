from django.db import models
from django.contrib.auth.models import User

class Track(models.Model):
    artist = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    audio_file = models.CharField(max_length=255)  # S3のURLを文字列で保存
    uploaded_at = models.DateTimeField(auto_now_add=True)
    play_count = models.PositiveIntegerField(default=0)

    # ローカル時間を文字列として返すプロパティ
    @property
    def local_uploaded_at_str(self):
        return self.uploaded_at.astimezone().strftime('%Y-%m-%d %H:%M:%S')

    def __str__(self):
        return self.title

class GoodTrack(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'track')

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class PlayHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    anonymous_id = models.CharField(max_length=255, null=True, blank=True)
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    played_at = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'anonymous_id', 'track', 'played_at')

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    icon = models.CharField(max_length=255, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    icon = models.CharField(max_length=255, blank=True)  # FileField から CharField に戻す
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Profile of {self.user.username}"

class Track(models.Model):
    artist = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    type = models.CharField(max_length=10, choices=[('audio', 'Audio'), ('image', 'Image')], blank=True)
    audio_file = models.CharField(max_length=255, blank=True, null=True)
    image_file = models.CharField(max_length=255, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    play_count = models.IntegerField(default=0)
    impression_count = models.IntegerField(default=0)
    comments = GenericRelation('Comment', related_query_name='track')

    def __str__(self):
        return self.title or "Untitled"

class Junction(models.Model):
    track = models.ForeignKey(Track, on_delete=models.CASCADE, related_name='junctions')
    parent_junction = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='child_junctions')
    collaborator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='junctions')
    title = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    type = models.CharField(max_length=10, choices=[('audio', 'Audio'), ('image', 'Image')])
    audio_file = models.CharField(max_length=500, blank=True, default="")
    image_file = models.CharField(max_length=500, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    play_count = models.IntegerField(default=0)
    impression_count = models.IntegerField(default=0)

    def __str__(self):
        return self.title or f"Untitled Junction by {self.collaborator.username}"

class GoodTrack(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    track = models.ForeignKey(Track, on_delete=models.CASCADE, null=True, blank=True)
    junction = models.ForeignKey(Junction, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [
            ('user', 'track'),
            ('user', 'junction'),
        ]

    def __str__(self):
        if self.track:
            return f"Good for Track {self.track.id} by User {self.user.username}"
        return f"Good for Junction {self.junction.id} by User {self.user.username}"

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content_type = models.ForeignKey('contenttypes.ContentType', on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.content_object}"

class PlayHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    anonymous_id = models.CharField(max_length=255, null=True, blank=True)
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    played_at = models.DateField()

class PlayRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    played_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'content_type', 'object_id', 'played_at']),
        ]

    def __str__(self):
        return f"Play by {self.user.username} on {self.content_object} at {self.played_at}"

class ImpressionRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    impressed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'content_type', 'object_id', 'impressed_at']),
        ]

    def __str__(self):
        return f"Impression by {self.user.username} on {self.content_object} at {self.impressed_at}"
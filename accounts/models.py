from django.db import models
from django.contrib.auth.models import User

class Snippet(models.Model):
    VISIBILITY_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    language = models.CharField(max_length=100)
    tags = models.CharField(max_length=255, blank=True)
    code = models.TextField()
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default='public')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

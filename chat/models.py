from django.db import models
from django.contrib.auth.models import User

class Chat(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="chat")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat for {self.user.username}"

class Message(models.Model):
    CHAT_TYPE_CHOICES = [
        ('human', 'Human'),
        ('ai', 'AI')
    ]

    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="messages")
    sender_type = models.CharField(max_length=10, choices=CHAT_TYPE_CHOICES)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender_type} - {self.content[:30]}"

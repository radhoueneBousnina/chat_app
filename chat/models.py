from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


# Create your models here.
class Room(models.Model):
    participants = models.ManyToManyField(User)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        participant_names = ' - '.join(
            [f"{user.first_name} {user.last_name}" if user.first_name and user.last_name else user.username for user in
             self.participants.all()])
        return f"Room: ({participant_names})"

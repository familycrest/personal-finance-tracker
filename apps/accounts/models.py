from secrets import token_hex
from typing import Self
from datetime import datetime

from django.db import models
from django.contrib.auth.models import AbstractUser
    
from base.settings import DEBUG

# Custom user model
class UserAccount(AbstractUser):
    # AbstractUser already includes username, email, first_name, last_name, password, etc.
    
    class Meta:
        db_table = "User_Accounts"
        verbose_name = "User Account"
        verbose_name_plural = "User Accounts"

    def __str__(self):
        return self.username
 
# # Notification type enum
# class NotificationType(models.TextChoices):
#     EMAIL = "EMAIL", "Email"
#     ALERT = "ALERT", "Alert"

# # Notification model
# class Notification(models.Model):
#     user = models.ForeignKey(UserAccount, on_delete=models.CASCADE, null=True, blank=True)
#     title = models.CharField(max_length=100)
#     message = models.TextField()
#     notification_type = models.CharField(
#         max_length=10, 
#         choices=NotificationType.choices,
#     )
#     creation_date = models.DateTimeField(auto_now_add=True)
#     is_read = models.BooleanField(default=False)


#     def __str__(self):
#         return f"{self.title} ({'Read' if self.is_read else 'Unread'})"

class AuthCode(models.Model):
    class Meta:
        db_table = "Temporary_Users"
        verbose_name = "Temporary User"
        verbose_name_plural = "Temporary Users"
        
    # The actual auth code, sent to the user's email
    code = models.CharField(max_length=6)

    # A session token to ensure that auth is done on the same browser
    # This will be removed once migrations are consolidated
    session_token = models.CharField(max_length=6, default="nocode")

    # When the token was created and issued
    issued = models.DateTimeField(auto_now=True)

    # Reference to the user who is being authenticated
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    
    @classmethod
    def create_from_user_account(cls, user: UserAccount) -> Self:
        code = token_hex(3).upper()
        session_token = token_hex(3).upper()
        
        obj, _ = cls.objects.update_or_create(
            user=user,
            defaults={
                "code": code,
                "session_token": session_token,
                "issued": datetime.now(),
                "user": user
            }
        )
        
        return obj

    def send_verif_email(self):
        if DEBUG:
            print(f"DEBUG MODE: Auth code is: {self.code}")
        else:
            # TODO: Integrate with SES
            print(f"Email integration is incomplete, here's the code to paste in: {self.code}")
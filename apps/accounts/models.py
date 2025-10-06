from secrets import token_hex
from typing import Self
from datetime import datetime

from django.db import models
from django.contrib.auth.models import AbstractUser

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
        
    code = models.CharField(max_length=6)
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    issued = models.DateTimeField(auto_now=True)
    
    @classmethod
    def create_from_user_account(cls, user: UserAccount) -> Self:
        code = token_hex(3).upper()
        
        obj, _ = cls.objects.update_or_create(
            user=user,
            defaults={
                "user": user,
                "code": code,
                "issued": datetime.now()
            }
        )
        
        return obj

    def send_verif_email(self):
        code = self.code

        print(f"Email integration is incomplete, here's the code to paste in: {code}")
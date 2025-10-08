from datetime import datetime, timezone

from secrets import token_hex
from typing import Self
from datetime import datetime

from django.db import models
from django.contrib.auth.models import AbstractUser
    
from base.settings import DEBUG, AUTH_SESSION_MAX_AGE

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
        
    # Reference to the user who is being authenticated
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)

    # The actual auth code, sent to the user's email
    code = models.CharField(max_length=6)

    # A session token to ensure that auth is done on the same browser
    # This will be removed once migrations are consolidated
    session_token = models.CharField(max_length=6, default="nocode")

    # When the token was created and issued
    issued = models.DateTimeField(auto_now=True)
    
    @classmethod
    def create_from_user_account(cls, user: UserAccount) -> Self:
        code = token_hex(3).upper()
        session_token = token_hex(3).upper()
        
        try:
            # Check if there is an existing one for the user
            existing_code = cls.objects.get(user=user)
        except cls.DoesNotExist:
            # Create a new one if there is none
            new_code = cls.objects.create(
                user=user,
                code=code,
                session_token=session_token,
                issued=datetime.now(),
            )
            return new_code
            
        # If there is one...
        time_since_issued = datetime.now(timezone.utc) - existing_code.issued
        if time_since_issued < AUTH_SESSION_MAX_AGE:
            # Do nothing and raise error if the existing code hasn't expired yet
            raise AuthSessionExistsException()
        else:
            # Replace it if it's past expiration
            existing_code.delete()
            new_code = cls.objects.create(
                user=user,
                code=code,
                session_token=session_token,
                issued=datetime.now(),
            )
            return new_code

    def send_verif_email(self):
        if DEBUG:
            print(f"DEBUG MODE: Auth code is: {self.code}")
        else:
            # TODO: Integrate with SES
            print(f"Email integration is incomplete, here's the code to paste in: {self.code}")

class AuthSessionExpiredException(Exception):
    pass

class AuthSessionExistsException(Exception):
    pass

from datetime import datetime, timezone, timedelta, date
from decimal import Decimal
from secrets import token_hex
from typing import Self

from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.conf import settings as cfg
from django.template.loader import get_template

from base.settings import EMAIL_BACKEND as EmailBackend
from apps.finances.models import EntryType, Category, Entry, AccountGoal, CategoryGoal


# Custom user model
class UserAccount(AbstractUser):
    # AbstractUser already includes username, email, first_name, last_name, password, etc.
    
    class Meta:
        db_table = "User_Accounts"
        verbose_name = "User Account"
        verbose_name_plural = "User Accounts"

    def __str__(self):
        return self.username
    def get_categories(self) -> models.QuerySet:
        """Return all of the categories related to an account."""
        return Category.objects.filter(user=self)
    
    def add_category(self, name: str, entry_type: EntryType, description: str = None) -> Category:
        """Create a category that belongs to the UserAccount."""
        # Check that the string inputs are of the correct type
        if not isinstance(name, str):
            raise TypeError("name must be a string")
        if description is not None and not isinstance(description, str):
            raise TypeError("description must be a string")
        
        # Try to create and save a category object
        try:
            category = Category(
                user=self,
                name=name,
                description=description,
                entry_type=entry_type
            )
            category.full_clean()
            category.save()
        # If user or name is too long this will be raised.
        except ValidationError as e:
            raise ValueError(str(e))
        
        return category
    
    def remove_category(self, name: str) -> Category:
        """Remove a category that belongs to a UserAccount by the name."""
        if not isinstance(name, str):
            raise TypeError("Name must be a string")
        try:
            category = Category.objects.get(user=self, name=name)
            category.delete()
            return category
        except Category.DoesNotExist:
            return None

    def get_notifications(self) -> models.QuerySet:
        """Return all the notifications related to an account."""
        return Notification.objects.filter(user=self)

    def add_notification(self, title: str, message: str):
        """Create a notification that belongs to the UserAccount."""
        # Check that the string inputs are of the correct type
        if not isinstance(title, str):
            raise TypeError("title must be a string")
        if message is not None and not isinstance(message, str):
            raise TypeError("message must be a string")
            
        # Try to create and save a notification object
        try:
            notification = Notification(
                user=self,
                title=title,
                message=message,
                creation_date=datetime.now(timezone.utc)
            )
            notification.full_clean()
            notification.save()
        # If user or name is too long this will be raised.
        except ValidationError as e:
            raise ValueError(str(e))
        
        return notification
    
    def remove_notification(self, _type: str):
        """Remove a notification that belongs to a UserAccount by its type."""
        try:
            notification = Notification.objects.get(user=self, _type=_type)
            notification.delete()
            return notification
        except Notification.DoesNotExist:
            return None

    #def get_goals(self) -> models.QuerySet:
    #    """Return all of the goals under an account."""
    #    return CategoryGoal.objects.filter(user=self)

    def get_account_goals(self) -> models.QuerySet:
        """Return all of the account goals under an account."""
        return AccountGoal.objects.filter(user=self)

    def check_all_goals(self, balance):
        """Check and send notifications for all the goals and account goals for an account."""

        all_goals = self.get_account_goals() #+ self.get_goals()
        for goal in all_goals:
            print(f"scan :: on goal, bal {balance}, {goal.amount}")

            if goal.entry_type == "EXPENSE":
                balance = -balance

            if balance > float(goal.amount):
                print("scan :: add exceed")
                self.add_notification(
                    f"{goal.name}: You've exceeded this goal!",
                    f"You've exceeded '{goal.name}' in the latest transaction."
                )
            elif balance > float(goal.amount) * 0.9:
                print("scan :: add almost")
                self.add_notification(
                    f"{goal.name}: Almost there!",
                    f"You're within 10% of '{goal.name}'!"
                )

    def get_balance(self):
        entries = Entry.objects.filter(user=self)
        income = entries.filter(entry_type=EntryType.INCOME).aggregate(total=models.Sum("amount"))["total"] or 0
        expense = entries.filter(entry_type=EntryType.EXPENSE).aggregate(total=models.Sum("amount"))["total"] or 0

        return income - expense
 
# # Notification type enum
# class NotificationType(models.TextChoices):
#     EMAIL = "EMAIL", "Email"
#     ALERT = "ALERT", "Alert"

class Notification(models.Model):
    class Meta:
        db_table = "Notifications"
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"

    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=128)
    message = models.TextField()
    # notification_type = models.CharField(
    #    max_length=10, 
    #    choices=NotificationType.choices,
    # )
    creation_date = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} ({'Read' if self.is_read else 'Unread'}): {self.message}"

class AuthSession(models.Model):
    class Meta:
        db_table = "Auth_Sessions"
        verbose_name = "Authentication Session"
        verbose_name_plural = "Authentication Sessions"
        
    # Reference to the user who is being authenticated
    user = models.ForeignKey(cfg.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # The actual auth code, sent to the user's email
    code = models.CharField(max_length=6)

    # A session token to ensure that auth is done on the same browser
    session_token = models.CharField(max_length=32)

    # When the token was created and issued
    issued = models.DateTimeField(auto_now=True)

    @classmethod
    def clean_up_old_sessions(cls):
        # Check for and clean up expired auth sessions
        for session in cls.get_queryset().iterator():
            if session.is_expired():
                session.delete()
    
    @classmethod
    def create_from_user_account(cls, user: cfg.AUTH_USER_MODEL) -> Self:
        code = token_hex(3).upper()
        session_token = token_hex(16).upper()
        
        try:
            # Check if there is an existing one for the user
            existing_session = cls.objects.get(user=user)
        except cls.DoesNotExist:
            # Create a new one if there is none
            session = cls.objects.create(
                user=user,
                code=code,
                session_token=session_token,
                issued=datetime.now(timezone.utc),
            )
            return session
            
        # If there is one...
        if existing_session.age() < cfg.AUTH_SESSION_MAX_AGE:
            # Do nothing and raise error if the existing code hasn't expired yet
            raise AuthSessionExistsException()
        else:
            # Replace it if it's past expiration
            existing_session.delete()
            session = cls.objects.create(
                user=user,
                code=code,
                session_token=session_token,
                issued=datetime.now(timezone.utc),
            )
            return session

    def send_verif_email(self):
        if cfg.DEBUG:
            print(f"DEBUG MODE: Auth code is: {self.code}")

        if cfg.EMAIL_AUTHENTICATION:
            subject = f"{self.user.username}, here's your authentication code for the Personal Finance Tracker."
            template = get_template("auth_code.html")
            context = {"auth_code": self.code}
            html_body = template.render(context)
            text_body = f"Your authentication code is: {self.code}. Please do not share this code with anyone."        

            EmailBackend().send_email(
                cfg.EMAIL_AUTHENTICATION_ADDRESS,
                self.user.email,
                subject,
                text_body,
                html_body
            )
    
    def verify_against_code(self, code: str) -> bool:
        return self.code == code
    
    def age(self) -> timedelta:
        return datetime.now(timezone.utc) - self.issued 

    def is_expired(self) -> bool:
        return self.age() >= cfg.AUTH_SESSION_MAX_AGE

class AuthSessionExpiredException(Exception):
    pass

class AuthSessionExistsException(Exception):
    pass

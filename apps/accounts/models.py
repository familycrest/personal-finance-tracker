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
from apps.finances.models import EntryType, Category, Entry, AccountGoal


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
        

    def get_entries(self, entry_type: EntryType | str, start_date: date | None = None, end_date: date | None = None) -> models.QuerySet:
        """
        Get all of a user's entries of a certain EntryType within a certain time period regardless of category.
        Both start_date and end_date are optional. It is best to enter an EntryType object to avoid errors,
        but you can also input "INCOME" or "EXPENSE"."""
        # Check that entry_type is a valid EntryType
        try:
            entry_type = EntryType(entry_type)
        except ValueError:
            raise ValueError("entry_type argument must be 'INCOME' or 'EXPENSE'")
        
        # Check that start date is less than or equal to end date if they are both entered.
        if start_date and end_date and start_date > end_date:
            raise ValueError("start_date must be <= end_date")
        
        # Return a query set of entries based on the entered criteria.
        query_set = Entry.objects.filter(user=self, entry_type=entry_type)
        if start_date:
            query_set = query_set.filter(date__gte=start_date)
        if end_date:
            query_set = query_set.filter(date__lte=end_date)

        return query_set
    
    def add_account_goal(self, name: str, description: str, entry_type: EntryType, start_date: date, end_date: date, amount: Decimal) -> AccountGoal:
        """Create an AccountGoal for user. Raises a ValueError if start_date > end_date or full_clean() object validation fails."""
        # Check start_date <= end_date
        if not start_date <= end_date:
            raise ValueError("start_date must be <= end_date")
        
        # Try to add an account goal, otherwise raise a value error
        try:
            account_goal = AccountGoal(
                user=self,
                name=name,
                description=description,
                entry_type=entry_type,
                start_date=start_date,
                end_date=end_date,
                amount=amount
            )
            account_goal.full_clean()
            account_goal.save()
            return account_goal
        except ValidationError as e:
            raise ValueError(str(e))

    def remove_account_goal(self, name: str) -> AccountGoal | None:
        if not isinstance(name, str):
            raise TypeError("name must be of type str")
        
        try:
            account_goal = AccountGoal.objects.filter(user=self, name=name).get()
            account_goal.delete()
            return account_goal
        except AccountGoal.DoesNotExist:
            return None
        
    def get_account_goals(self) -> models.QuerySet:
        """Return all account goals for the user."""
        goals = AccountGoal.objects.filter(user=self)
        
        if len(goals) > 0:
            return goals
        else:
            return None

 
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

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

    def add_notification(self, title: str, msg_text: str = "", msg_list: list = []):
        """Create a notification that belongs to the UserAccount."""
        # Check that the string inputs are of the correct type
        if not isinstance(title, str):
            raise TypeError("title must be a string")
            
        # Try to create and save a notification object
        try:
            notification = Notification(
                user=self,
                title=title,
                message={
                    "text": msg_text,
                    "list": msg_list
                },
                creation_date=datetime.now(timezone.utc)
            )
            notification.full_clean()
            notification.save()
        # If user or name is too long this will be raised.
        except ValidationError as e:
            raise ValueError(str(e))
        
        return notification
    
    def get_category_goals(self) -> models.QuerySet:
        """Return all of the goals under an account."""
        return CategoryGoal.objects.filter(category__user=self)

    def get_account_goals(self) -> models.QuerySet:
        """Return all of the account goals under an account."""
        return AccountGoal.objects.filter(user=self)

    def check_all_goals(self):
        """Check and send notifications for all the goals and account goals for an account."""
        
        balance = self.get_balance()

        def scan(balance, goals):
            """Scans through a set of Category/AccountGoal objects and returns a list of ones worthy of notification."""

            out = []

            for goal in goals:
                corrected_bal = balance * (-1 if goal.entry_type == "EXPENSE" else 1)
                print(f"account goal {goal.name}, {goal.entry_type}, {goal.amount}, corrected {corrected_bal}")

                if corrected_bal > float(goal.amount):
                    print(f"{goal.name} exceed")
                    out.append({"name": goal.name, "type": goal.entry_type, "exceeded": True})
                elif corrected_bal > float(goal.amount) * 0.9:
                    print(f"{goal.name} almost")
                    out.append({"name": goal.name, "type": goal.entry_type, "exceeded": False, "amount": goal.amount})

            return out

        def generate_goal_msg(balance, goal, show_goal_name = True):
            """Generates a message based on the goal, whether it's an expense or income, and its status."""

            msg = f"{goal["name"]}: " if show_goal_name else ""

            if goal["exceeded"]:
                # Exceeded goal
                if goal["type"] == "EXPENSE":
                    return msg + "‼️ You've gone overbudget!"
                else:
                    return msg + "🎉 You've outdone yourself - great job!"
            else:
                # Goal within 10%
                if goal["type"] == "EXPENSE":
                    difference = goal["amount"] + balance

                    if difference == 0:
                        return msg + "⚠️ You've maxed out this budget."
                    else:
                        return msg + f"⚠️ You are ${difference:.2f} of maxing out this budget."
                else:
                    difference = goal["amount"] - balance
                    return msg + f"📈 You're almost there, just ${difference:.2f} left to go!"
        
        def generate_notifs(balance, goals, goal_type):
            """Generates notifications for goals worthy of notification."""
            goals = scan(balance, goals)

            if len(goals) > 1:
                # Generate a list of alerts if there are multiple goals, instead of firing one notification per goal
                self.add_notification(
                    f"Alerts for your {goal_type} goals",
                    msg_text="These goals have been affected by the latest transaction: ",
                    msg_list=[generate_goal_msg(balance, goal) for goal in goals]
                )
            elif len(goals) == 1:
                # Send a single notification if there's only one
                goal = goals[0]
                self.add_notification(
                    f"{goal_type.title()} goal alert for '{goal["name"]}'",
                    msg_text=generate_goal_msg(balance, goal, False)
                )

        # Don't Repeat Yourself, they say
        generate_notifs(balance, self.get_account_goals(), "account")
        generate_notifs(balance, self.get_category_goals(), "category")

    def get_balance(self):
        entries = Entry.objects.filter(user=self)

        if len(entries) == 1:
            single = entries.first()
            return single.amount * (-1 if single.entry_type == "EXPENSE" else 1)
        else:
            income = entries.filter(entry_type=EntryType.INCOME).aggregate(total=models.Sum("amount"))["total"] or 0
            expense = entries.filter(entry_type=EntryType.EXPENSE).aggregate(total=models.Sum("amount"))["total"] or 0

        return income - expense

class Notification(models.Model):
    class Meta:
        db_table = "Notifications"
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"

    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=128)
    """
    Schema for this field:

        {
            text: str,
            list: [str]
        }
    
    Both fields are optional. `text` is rendered in a `<p>`, with a placeholder if unset. `list` is rendered as a `<ul>`.
    """
    message = models.JSONField()
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

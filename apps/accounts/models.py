from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from apps.finances.models import Category, EntryType

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

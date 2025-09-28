from accounts.models import UserAccount, Category, Entry, Goal, Notification 
from django.utils import timezone
from datetime import date

# 1. Create a sample user
user, created = UserAccount.objects.get_or_create(
    username="Fat",
    defaults={
        "email":"zadofo@example.com",
        "first_name": "Fatima",
        "last_name": "Zaid",
    },
)

user.set_password("testpassword123") # set a password
user.save()
print(f"[OK] User created:{user.username}")

# 2. Add categories 
categories_data = [
    ("Salary", "income"),
    ("Freelance", "income"),
    ("Groceries", "expense"),
    ("Rent", "expense"),
    ("Utilities", "expense"),  
]

categories ={}
for name, entry_type in categories_data:
    cat, _ = Category.objects.get_or_create(
        user=user,
        name=name,
        entry_type=entry_type.upper()
    )
    categories[name] = cat
    print(f"[OK] Category added:{name}")

# 3. Add transactions (Entries)
entries_data = [
    ("Salary", 3000.00, "2025-09-01", "Monthly Salary", "income"),
    ("Freelance", 800.00, "2025-09-05", "Freelance Project", "income"),
    ("Groceries", 150.75, "2025-09-06", "Grocery Shopping", "expense"),
    ("Rent", 1200.00, "2025-09-03", "September Rent", "expense"),
    ("Utilities", 90.00, "2025-09-04", "Electricity Bill", "expense"),    
]

for name, amount, dt, desc, entry_type in entries_data:
    Entry.objects.get_or_create(
        user=user,
        category=categories[name],
        name=name,
        amount=amount,
        date=date.fromisoformat(dt),
        entry_type=entry_type.upper(),
        description=desc,
    )
    print(f"[OK] Entry added:{name}{amount}")

# 4. Add goals
goals_data = [
    ("Grocery Budget", "Keep grocery expenses under $ 500 for September", "expense", "2025-09-01", "2025-09-30", 500.00, "Groceries"),
    ("Rent Payment", "Ensure rent is paid in full for September", "expense", "2025-09-01", "2025-09-30", 1200.00, "Rent"),
    ("Salary Savings", "Save at least $1000 from monthly salary", "income", "2025-09-01", "2025-09-30", 1000.00, "Salary"),
]

for name, desc, entry_type, start, end, amount, cat_name in goals_data:
    Goal.objects.get_or_create(
        user=user,
        category=categories[cat_name],
        name=name,
        description=desc,
        entry_type=entry_type.upper(),
        start_date=date.fromisoformat(start),
        end_date=date.fromisoformat(end),     
        amount=amount,
    )
    print(f"[OK] Goal added:{name}")

 # 5. Add notifications
notifications_data = [
    ("Budget Alert", "ALERT", "You have exceeded your Grocery Budget for September.", False),
    ("Goal Reminder", "EMAIL", "Remember to save at least $1000 from your Salary this month.", False),
    ("Payment Confirmation", "EMAIL", "Your Rent payment for September has been recorded.", True),
]

for title, ntype, message, is_read in notifications_data:
    Notification.objects.get_or_create(
        user=user,
        title=title,
        notification_type=ntype,
        message=message,
        is_read=is_read,
        creation_date=timezone.now(),          
    )
    print(f"[OK] Notification added:{title}")

print("[OK] Seeding completed Successfully.")


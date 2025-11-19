from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.finances.models import *
from datetime import datetime
from dateutil.relativedelta import relativedelta
from random import random, triangular
from decimal import Decimal


class Command(BaseCommand):
    help = "Populates the database with testing data for manual testing. Do not run in a database with production data."

    def handle(self, *args, **options):
        user = populate_users()
        populate_categories(user)
        populate_transactions(user)


def populate_users():
    """Create superuser for testing."""
    # Create superuser
    user, created = get_user_model().objects.get_or_create(
        username="admin",
        defaults={
            "email":"email@email.com",
            "first_name": "John",
            "last_name": "Doe",
            "is_superuser": True,
            "is_staff": True,
            "is_active": True,
        }
    )
    if created:
        user.set_password("adminpassword")
        user.save()

    return user


def populate_categories(user):
    cats = [
        ("Gas", "EXPENSE"),
        ("Groceries", "EXPENSE"),
        ("Fun", "EXPENSE"),
        ("Insurance", "EXPENSE"),
        ("Utilites", "EXPENSE"),
        ("Machine Shop", "INCOME"),
        ("Programming", "INCOME"),
        ("Odd Jobs", "INCOME"),
        ("Vending Machines", "INCOME"),
        ("Laundromat", "INCOME"),
    ]

    for c in cats:
        cat, created = Category.objects.get_or_create(
            user = user,
            name = c[0],
            entry_type = c[1],
        )
        if created:
            cat.save()


def populate_transactions(user):
    cats = Category.objects.filter(user=user)

    # Set amount limits that make sense for categories. The first value is the base amount for randomly generated amounts,
    # the second is the max. The third value is the chance it will be generated on a given day.
    amounts = {
        "Gas": (20, 70, 1.0/7),
        "Groceries": (10, 120, 1.5/7),
        "Fun": (10, 200, 1.0/7),
        "Insurance": (100, 200, 1.0/30),
        "Utilites": (100, 200, 1.0/30),
        "Machine Shop": (300, 1000, 1.0/14),
        "Programming": (1000, 1000, 1.0/30),
        "Odd Jobs": (100, 1000, 1.0/60),
        "Vending Machines": (100, 500, 1.0/14),
        "Laundromat": (500, 2000, 1.0/14)
    }
    end_date = datetime.today()
    current_date = end_date - relativedelta(years=2) + relativedelta(days=1)

    while current_date <= end_date:
        for cat in cats:
            name = cat.name
            base_amount = amounts[name][0]
            max_amount = amounts[name][1]
            # Generate a random amount for the tranaction between the two values (inclusive)
            amount = triangular(base_amount, max_amount)
            amount=Decimal(f"{amount:.2f}")
            fate = random()
            chance = amounts[name][2]
            # If the randomly generated number is less than the chance make a transaction
            if fate < chance:
                transaction, created = Entry.objects.get_or_create(
                    user=user,
                    category=cat,
                    name=f"{name}-{fate+1:.3f}",
                    defaults={
                        "description": "Lorem ipsum, dolor sit amet consectetur adipisicing elit. Necessitatibus mollitia pariatur blanditiis consectetur facere facilis odio. Eius pariatur mollitia quo doloribus, corporis reprehenderit fuga qui sunt natus magni aut magnam?",
                        "entry_type": cat.entry_type,
                        "amount": amount,
                        "date": current_date,
                    },
                )
                if created:
                    transaction.save()

        current_date += relativedelta(days=1)




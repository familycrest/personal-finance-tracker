from datetime import date, timedelta, datetime
from dateutil.relativedelta import relativedelta
from .models import Entry, EntryType, Category, AccountGoal, CategoryGoal
from decimal import Decimal
import math



def generate_report(user, start_date: date, end_date: date, interval: str, category: Category = None):
    """
    Returns a list of sums for each chosen interval of all transactions or a category's transactions between a
    start date and an end date including the start and end dates.
    This is returned as a dictionary in the form of:
    {"date_str": {EntryType.EXPENSE: Decimal("0"), EntryType.INCOME: Decimal("0")}

    Possible values for interval are "day", "week", or "month".
    Date Strings:
    "day": "%m/%d/%Y"
    "week": "%W/%Y"
    "month": "%m/%Y"
    """
    # Test code
    # start_date = datetime(2025,10,2)
    # end_date = datetime(2025,11,1)

    # Get transactions between and including the start and end dates for the user
    if category:
        transactions = Entry.objects.filter(user=user, category=category, date__gte=start_date, date__lte=end_date)
    else:
        transactions = Entry.objects.filter(user=user, date__gte=start_date, date__lte=end_date)
    transaction_data = {}

    # Setup dictionary of values for each chosen interval even if there are no transactions for that interval for graphing purposes
    # Add one to include start date in length
    DAYS = (end_date - start_date).days + 1
    if interval == "day":
        format_str = "%m/%d/%Y"
        transaction_data = {(start_date + timedelta(days=i)).strftime(format_str): {EntryType.EXPENSE: Decimal("0"), EntryType.INCOME: Decimal("0")} for i in range(DAYS)}
    elif interval == "week":
        format_str = "%W/%Y"
        weeks = math.ceil(DAYS / 7)
        transaction_data = {(start_date + relativedelta(weeks=i)).strftime(format_str): {EntryType.EXPENSE: Decimal("0"), EntryType.INCOME: Decimal("0")} for i in range(weeks)}
    elif interval == "month":
        format_str = "%m/%Y"
        cur_year = start_date.year
        cur_month = start_date.month
        end_year = end_date.year
        end_month = end_date.month
        while (cur_month <= end_month) or (cur_year < end_year):
            transaction_data[f"{cur_month:02}/{cur_year}"] = {EntryType.EXPENSE: Decimal("0"), EntryType.INCOME: Decimal("0")}
            if cur_month < 12:
                cur_month += 1
            else:
                cur_month = 1
                cur_year += 1

    else:
        raise ValueError(f"incorrect interval argument: {interval}")
    
    for tran in transactions:
        date = tran.date.strftime(format_str)
        entry_type = tran.entry_type
        amount = tran.amount
    
        transaction_data[date][entry_type] += amount
    
    return transaction_data


# def generate_category_report(self, category: Category, start_date: date, end_date: date, interval: str):
#     # Add one to account for the start date and end date being included
#     TIME_LENGTH = (end_date - start_date).days + 1

#     if interval.lower() == "day":
#         interval_len = 7

#     # Create a dictionary of all days in the time period requested with the value representing the sum of transactions of the category's type
#     day_data = {(end_date - timedelta(days=i)): Decimal("0") for i in range(TIME_LENGTH)}
#     transactions = Entry.objects.filter(user=self.user, date__gte=start_date, date__lte=end_date)

#     # Populate the dictionary with the sums of all of the category's transactions for the date range
#     for transaction in transactions:
#         date = transaction.date
#         amount = transaction.amount
#         day_data[date] += amount

#     return day_data


# def check_account_goal_progress(self):
#     goal_progress = {}
#     goals = AccountGoal.objects.filter(user=self.user_account)
#     for goal in goals:
#         total_entries_amount = sum(
#             entry.amount for entry in Entry.objects.filter(
#                 user=self.user_account,
#                 entry_type=goal.entry_type
#             )
#         )
#         total_goal_amount = goal.amount
#         if total_goal_amount == 0:
#             percentage = 0
#         else:
#             percentage = (total_entries_amount / total_goal_amount) * 100

#         if percentage >= 100:
#             goal_progress[goal.id] = 100.0  
#         else:
#             goal_progress[goal.id] = float(round(percentage, 2))

#     return goal_progress

# def check_category_goal_progress(self):
#     goal_progress = {}
#     categories = Category.objects.filter(user=self.user_account)
#     for category in categories:
#         goal_percentages = category.get_goal_percentages()
#         category_goal_progress = {}
#         for goal, goal_percentage in goal_percentages.items():
#             if goal_percentage >= 100:
#                 category_goal_progress[goal.id] = 100.0  
#             else:
#                 category_goal_progress[goal.id] = float(round(goal_percentage, 2))
#         goal_progress[category.id] = category_goal_progress  

#     return goal_progress
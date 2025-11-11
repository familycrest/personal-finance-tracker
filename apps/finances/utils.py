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


def sort_by_date(date: str):
    """
    This function assumes date strings are in the format week#/year, month/year, or month/day/year.
    Returns a tuple to be the key for a sorting function like sorted.
    """
    keys = date[0].split('/')

    if len(keys) == 2:
        return (keys[1], keys[0])
    elif len(keys) == 3:
        return (keys[2], keys[0], keys[1])
    else:
        raise ValueError(f"invalid data string: {date}")
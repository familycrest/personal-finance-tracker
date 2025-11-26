from datetime import date
from dateutil.relativedelta import relativedelta
from .models import Entry, EntryType, Category
from decimal import Decimal


def generate_report(
    user,
    start_date: date,
    end_date: date,
    interval: str,
    category: Category = None,
):
    """
    Returns a dictionary sorted by date of sums for each chosen interval of all transactions or a category's transactions between a
    start date and an end date including the start and end dates.
    This is returned in the form of:
    {"date_str": {EntryType.EXPENSE: float, EntryType.INCOME: float}

    Possible values for interval are "day", "week", or "month".
    Date Strings:
    "day": "%m/%d/%Y"
    "week": "%W/%Y"
    "month": "%m/%Y"
    """

    # Get transactions between and including the start and end dates for the user
    if category:
        transactions = Entry.objects.filter(
            user=user,
            category=category,
            date__gte=start_date,
            date__lte=end_date,
        )
    else:
        transactions = Entry.objects.filter(
            user=user, date__gte=start_date, date__lte=end_date
        )
    transaction_data = {}

    # Setup dictionary of values for each chosen interval even if there are no transactions for that interval for graphing purposes
    # Add one to include start date in length
    DAYS = (end_date - start_date).days + 1
    if interval == "day":
        format_str = "%m/%d/%Y"
        transaction_data = {
            (start_date + relativedelta(days=i)).strftime(format_str): {
                EntryType.EXPENSE: Decimal("0"),
                EntryType.INCOME: Decimal("0"),
            }
            for i in range(DAYS)
        }
    elif interval == "week":
        format_str = "%W/%Y"
        weeks = set()
        cur_date = start_date
        # Create a set of weeks to sum up the data for. This way of creating weeks accounts for partial weeks
        # at the beginning and end of years and starting / ending in the middle of a week.
        while cur_date <= end_date:
            weeks.add(cur_date.strftime(format_str))
            cur_date += relativedelta(days=1)
        # Create the dictionary to hold sums with the keys being the week strings from the set
        transaction_data = {
            week: {
                EntryType.EXPENSE: Decimal("0"),
                EntryType.INCOME: Decimal("0"),
            }
            for week in weeks
        }
    elif interval == "month":
        format_str = "%m/%Y"
        cur_year = start_date.year
        cur_month = start_date.month
        end_year = end_date.year
        end_month = end_date.month
        # Create a dictionary of months from the starting month to the ending month taking into account years.
        # Months can be done this way because there are always 12 months. There can be 52 or 53 weeks and they
        # start and end on different days and with different lengths.
        while (cur_year < end_year) or (
            cur_year == end_year and cur_month <= end_month
        ):
            transaction_data[f"{cur_month:02}/{cur_year}"] = {
                EntryType.EXPENSE: Decimal("0"),
                EntryType.INCOME: Decimal("0"),
            }
            if cur_month < 12:
                cur_month += 1
            else:
                cur_month = 1
                cur_year += 1
    else:
        raise ValueError(f"incorrect interval argument: {interval}")

    # Sum the income and expense data for the given time range
    for tran in transactions:
        # Add to the correct date key. format_str converts days into their weeks or months or etc.
        date = tran.date.strftime(format_str)
        entry_type = tran.entry_type
        amount = tran.amount
        transaction_data[date][entry_type] += amount

    # Convert transaction data to float for display after more accurate decimal calculations
    for tran in transaction_data:
        transaction_data[tran][EntryType.EXPENSE] = float(
            transaction_data[tran][EntryType.EXPENSE]
        )
        transaction_data[tran][EntryType.INCOME] = float(
            transaction_data[tran][EntryType.INCOME]
        )
    # Sort dictionary by date
    transaction_data = dict(
        sorted(transaction_data.items(), key=lambda x: sort_by_date(x))
    )

    return transaction_data


def generate_pie_report(user, start_date: date, end_date: date, entry_type: EntryType):
    # Get a list of all the user's transactions in the date range within the entry type
    transactions = Entry.objects.filter(
        user=user,
        date__gte=start_date,
        date__lte=end_date,
        entry_type=entry_type,
    )

    cat_data = {}
    # Sum up each category's transactions
    for t in transactions:
        # Handle transactions without a category
        if t.category is None:
            cat = -1  # Use -1 as the key for uncategorized transactions
            cat_name = "No Category"
        else:
            cat = t.category.pk
            cat_name = t.category.name

        # If the category isn't in cat data, add it in with an amount of zero
        if cat not in cat_data:
            cat_data[cat] = [cat_name, Decimal("0")]

        # Add transaction amount to correct category
        cat_data[cat][1] += t.amount

    # Convert sums to floats then return list
    for c in cat_data:
        cat_data[c][1] = float(cat_data[c][1])

    return cat_data


def generate_savings_report(user, start_date: date, end_date: date, interval: str):
    # Get a list of all the user's transactions in the date range
    transactions = Entry.objects.filter(
        user=user, date__gte=start_date, date__lte=end_date
    ).order_by("date")

    # Determine the date format based on interval (same as generate_report)
    DAYS = (end_date - start_date).days + 1
    if interval == "day":
        format_str = "%m/%d/%Y"
        # Create data point for each day
        data_points = {
            (start_date + relativedelta(days=i)).strftime(format_str): Decimal("0")
            for i in range(DAYS)
        }
    elif interval == "week":
        format_str = "%W/%Y"
        # Create set of all weeks in the range
        weeks = set()
        cur_date = start_date
        while cur_date <= end_date:
            weeks.add(cur_date.strftime(format_str))
            cur_date += relativedelta(days=1)
        data_points = {week: Decimal("0") for week in weeks}
    elif interval == "month":
        format_str = "%m/%Y"
        # Create data point for each month
        data_points = {}
        cur_year = start_date.year
        cur_month = start_date.month
        end_year = end_date.year
        end_month = end_date.month
        while (cur_month <= end_month) or (cur_year < end_year):
            data_points[f"{cur_month:02}/{cur_year}"] = Decimal("0")
            if cur_month < 12:
                cur_month += 1
            else:
                cur_month = 1
                cur_year += 1
    else:
        raise ValueError(f"incorrect interval argument: {interval}")

    # Calculate cumulative net savings
    cumulative_savings = Decimal("0")
    for tran in transactions:
        if tran.entry_type == "INCOME":
            amount = tran.amount
        else:
            amount = -tran.amount
        cumulative_savings += amount

        # Update the cumulative savings at this interval
        date_key = tran.date.strftime(format_str)
        data_points[date_key] = cumulative_savings

    # Sort data_points by date
    data_points = dict(sorted(data_points.items(), key=lambda x: sort_by_date(x)))

    # Fill in intervals that had no transactions with the previous cumulative value
    previous_value = Decimal("0")
    for date_key in data_points.keys():
        if data_points[date_key] == Decimal("0") and previous_value != Decimal("0"):
            data_points[date_key] = previous_value
        previous_value = data_points[date_key]

    # Convert to list format
    result = []
    for date_key in data_points.keys():
        result.append([date_key, float(data_points[date_key])])

    return result


def sort_by_date(item):
    """
    This function takes a tuple in the form of (date_str, Decimal).
    This function assumes date strings are in the format week#/year, month/year, or month/day/year.
    Returns a tuple to be the key for a sorting function like sorted.
    """
    date_str = item[0]
    keys = date_str.split("/")

    if len(keys) == 2:
        return (keys[1], keys[0])
    elif len(keys) == 3:
        return (keys[2], keys[0], keys[1])
    else:
        raise ValueError(f"invalid date string: {date_str}")


def get_start_date(end_date: date, period: str):
    if period == "week":
        start_date = end_date - relativedelta(days=6)
    elif period == "month":
        start_date = end_date - relativedelta(months=1) + relativedelta(days=1)
    else:
        start_date = end_date - relativedelta(years=1) + relativedelta(days=1)

    return start_date

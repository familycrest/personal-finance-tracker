## Orignal UML Class Structure Issues: (Not about the one below)
- User:
  - User adds income and expenses to categories. This doesn't make any sense, because User only holds budgets and has no method to tell budget to add them to the category totals.
  - ~~Doesn't have a method to create or even call a method in an analytics object, nor does it hold a list of categories for it to be able to give the Analytics object.~~
    - Actually a controller could make analytics objects with the desired budget and categories, but it still shouldn't hold categories that the budgets already hold.

- Budget:
  - Budget doesn't have any way to hold individual expenses or salary. It can only add to a total of each of those. We need an entry / transaction object. But the same totals are in Category, too, which adds the risk of mismatching numbers and unnecessary complexity.
  - Budget doesn't even have a way to hold the actual budget, except when associated with a category. It has a categoryBudget attribute: Dict[Category, float], which makes no sense given you should ask the Category object what its budget is if you're holding it that way. But then the budget object is pointless!
  - Why do both Budget and Category hold total expenses and income? That should be the job of one of those.
  - Why is budget connected to reports? I don't think it should have a responsibility to create reports. It also doesn't have a method to do so.

- Category:
  - Shouldn't a category have budgets and not the other way around? The current way doesn't make sense, especially when you consider the category itself is associated with the actual number set for the budget and the budget only holds a list of numbers associated to categories.

- Analytics and Reports:
  - Analytics is the class that creates reports and bar graphs. However, analytics isn't connected to bar graph in the UML, and instead Report is. Even though report has no methods to create a graph or even an attribute to hold one.
  - ~~We need a more generic Graph class before a Bar Graph class.~~
    - Changed my mind on that.


```mermaid
classDiagram

class Account {
    - email: String
    - first_name: String
    - last_name: String
    - categories: List~Category~
    - account_goals: List~Goal~
    - notifications: List~Notification~

    + Account(email: String, first_name: String, last_name: String)
    + get_email() String
    + get_first_name() String
    + get_last_name() String
    + get_categories(entry_type: EntryType) List~Category~
    + add_category(name: String, description: String, entry_type: EntryType) Boolean
    + remove_category(name: String) Boolean
    + get_entries(entry_type: EntryType, start_date: date, end_date: date) List~Entry~
    + add_account_goal(name: String, description: String, entry_type: EntryType, start_date: Date, end_date: Date, amount: Decimal) Boolean
    + remove_account_goal(name: String) Boolean
    + get_account_goals() List~Goal~
    + get_account_goal_percentages() Dict~Goal, float~
    + get_notifications() List~Notification~
    + add_notification(notification: Notification) Boolean
    + remove_notification(name: String) Boolean
    + clear_notifications() Boolean

}

class AuthenticationService {
    + create_temp_account(email: String, password: String, first_name: String, last_name: String)
    + send_verif_email(email: String, code: String) Boolean
    + verify_email_code(email: String, code: String) Boolean
    + activate_account(email: String) Boolean
    + verify_credentials(email: String, password: String) Boolean
    + is_account_verified(email: String) Boolean

}

class Category {
    - name: String
    - description: String
    - entry_type: EntryType
    - entries: List~Entry~
    - goals: List~Goal~


    + Category(name: String, description: String, entry_type: EntryType)
    + get_name() String
    + get_description() String
    + get_entry_type() EntryType
    + get_entries() List~Entry~
    + add_entry(name: String, description: String, entry_type: EntryType, date: Date, amount: Decimal) Boolean
    + remove_entry(name: String) Boolean
    + get_goals() List~Goal~
    + add_goal(name: String, description: String, entry_type: EntryType, start_date: Date, end_date: Date, amount: Decimal) Boolean
    + remove_goal(name: String) Boolean
    + get_total() Decimal
    + get_goal_percentages() Dict~Goal, float~
}

class EntryType {
    <<enumeration>>
    + INCOME: String
    + EXPENSE: String
}

class Entry {
    - name: String
    - description: String
    - entry_type: EntryType
    - date: Date
    - amount: Decimal

    + Entry(name: String, description: String, entry_type: EntryType, date: Date, amount: Decimal)
    + get_name() String
    + get_description() String
    + get_entry_type() EntryType
    + get_date() Date
    + get_amount() Decimal
}

class Goal {
    - name: String
    - description: String
    - entry_type: EntryType
    - start_date: Date
    - end_date: Date
    - amount: Decimal

    + Goal(name: String, description: String, entry_type: EntryType, start_date: Date, end_date: Date, amount: Decimal)
    + get_name() String
    + get_description() String
    + get_entry_type() EntryType
    + get_start_date() Date
    + get_end_date() Date
    + get_amount() Decimal
}

class NotificationType {
    <<enumeration>>
    + EMAIL: String
    + ALERT: String
}

class Notification {
    - title: String
    - message: String
    - notification_type: NotificationType
    - creation_date: Date

    + Notification(title: String, message: String, notification_type: NotificationType, creation_date: date)
    + get_title() String
    + get_message() String
    + get_notification_type() NotificationType
    + get_creation_date() Date
}

class NotificationService {
    + send_email_notification(account: Account, notification: Notification) Boolean
    + send_alert_notification(account: Account, notification: Notification) Boolean
}

class BarGraph {
    - title: String
    - description: String
    - data: Dict~String, Decimal~
    - creation_date: Date

    + BarGraph(title: String, description: String, data: Dict~String, Decimal~, creation_date: Date)
    + get_title() String
    + get_description() String
    + generate_bar_graph() Boolean
}


class Report {
    - title: String
    - message: String
    - creation_date: Date
    - graphs: List~BarGraph~

    + Report(title: String, message: String, creation_date: Date)
    + get_title() String
    + get_message() String
    + get_creation_date() Date
    + get_graphs() List~BarGraph~
}

class Analytics {
    - account: Account
    - creation_date: Date
    - reports: List~Report~

    + Analytics(account: Account, creation_date: Date)
    + get_account() Account
    + get_creation_date() Date
    + get_reports() List~Report~
    + generate_spending_report(start_date: Date, end_date: Date) Report
    + generate_category_report(category: Category, start_date: Date, end_date: Date) Report
    + check_goal_progress() List~Notification~
}


Account <.. AuthenticationService
Account o-- Category
Account o-- Goal
Account o-- Notification
Account <.. Analytics
Category o-- Entry
Category o-- Goal
EntryType <.. Entry
EntryType <.. Account
EntryType <.. Category
EntryType <.. Goal
NotificationType <.. Notification
Notification <.. NotificationService
Notification <.. Analytics
Analytics o-- Report
Report o-- BarGraph
```
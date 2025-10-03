# UML Class Diagram V3

## Diagram

```mermaid
classDiagram

class EmailService {
    + EmailService(boto3_client, sender_email_address: String)
    + send_email(destination_email_address: String, subject: String, contents: String)
}
class TempAccount {
    <<extends Django.User>>
    - auth_code: String
    + TempAccount(email: String, password: String, first_name: String, last_name: String, auth_code: String)
}

class UserAccount {
    <<extends Django.User>>
    - categories: List~Category~
    - account_goals: List~Goal~
    - notifications: List~Notification~
    - auth_code: String

    + UserAccount(email: String, password: String, first_name: String, last_name: String, auth_code: String)
    + UserAccount(temp_account: TempAccount)

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
    + create_temp_account(email: String, password: String, first_name: String, last_name: String, auth_code: String)
    + send_verif_email(email: String, code: String) Boolean
    + verify_email_code(email: String, code: String) Boolean
    + activate_account(temp_account: TempAccount) Boolean
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
    + send_email_notification(account: UserAccount, notification: Notification) Boolean
    + send_alert_notification(account: UserAccount, notification: Notification) Boolean
}

class BarGraph {
    - title: String
    - description: String
    - data: Dict~String, Decimal~
    - creation_date: Date

    + BarGraph(title: String, description: String, data: Dict~String, Decimal~, creation_date: Date)
    + get_title() String
    + get_description() String
    + get_creation_date() Date
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
    - user_account: UserAccount
    - creation_date: Date
    - reports: List~Report~

    + Analytics(user_account: UserAccount, creation_date: Date)
    + get_user_account() UserAccount
    + get_creation_date() Date
    + get_reports() List~Report~
    + generate_account_report(start_date: Date, end_date: Date) Report
    + generate_category_report(category: Category, start_date: Date, end_date: Date) Report
    + check_goal_progress() List~Notification~
}

TempAccount <.. AuthenticationService
UserAccount <.. AuthenticationService
UserAccount o-- Category
UserAccount o-- Goal
UserAccount o-- Notification
UserAccount <.. Analytics
Category o-- Entry
Category o-- Goal
EntryType <.. Entry
EntryType <.. UserAccount
EntryType <.. Category
EntryType <.. Goal
NotificationType <.. Notification
Notification <.. NotificationService
Notification <.. Analytics
Analytics o-- Report
Report o-- BarGraph

```


## Notes

### Changes to `Account` and `UserAccount`

They now extend Django's user authentication and storage system, which also handles session tokens.

### What's the signup/login process like? 
```

user asks for signup page
  < send back signup page with form
user submits signup form
  < send the "code entry" page
    ! set temp session cookie in request
  < send email with auth code
user enters auth code into "code entry" page
user submits form, along with session cookie
  ! if session cookie is still valid
    < redirect user to dashboard
      ! remove session cookie and replace with proper login cookie in request
    otherwise
    < redirect user back to signup page

? if the user signs up again with an existing TempAccount email:

- update the password and credentials
- set a new expiration date
- send a new code

? if the user signs up again with an existing email address:

- warn and ask them to login

? there'll be a button for the user to request a new auth code after a few minutes (as long as they keep the page open)

user asks for login page
  < send back login page with form
user submits login form
  ! if user credentials are valid
    < send the "code entry" page
      ! set temp session cookie in request
    < send email with auth code
user enters auth code into "code entry" page
user submits form, along with session cookie
  ! if session cookie is still valid
    < redirect user to dashboard
      ! remove session cookie and replace with proper login cookie in request
    otherwise
    < redirect user to signup page

```

### Why an email service?

The job of `EmailService` is simply to handle all of the interaction with AWS' email API and hide it behind a simple function that `AuthenticationService.send_verif_email()` and `NotificationService.send_email_notification()` can then use.

from django.test import override_settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth import get_user_model

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions

# from webdriver_manager.core.os_manager import ChromeType
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select

# from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from apps.accounts.models import AuthSession
from apps.finances.models import Entry, EntryType, Category

Users = get_user_model().objects

TEST_USER_CREDENTIALS = {
    "username": "selenium_test1",
    "email": "selenium@test-users.com",
    "password": "goodPASS1612",
}


# Contains driver setup/teardown methods and common methods that could be used in several classes
@override_settings(DUMMY_AUTH_BACKEND_QUIET=True)
class BaseSeleniumTest(StaticLiveServerTestCase):
    # Driver setup
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        chrome_options = ChromeOptions()
        # Comment/uncomment the line below to toggle headless testing
        # chrome_options.add_argument("--headless")

        cls.driver = webdriver.Chrome(
            service=ChromeService("/usr/bin/chromedriver"),
            options=chrome_options,
        )
        cls.wait = WebDriverWait(cls.driver, 5)

    # Driver teardown
    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()

    def path(self, path):
        """
        Converts a relative path into an absolute path, which includes the
        server's hostname.
        Example: `/finances/dashboard` -> `https://parfait.app/finances/dashboard`
        """
        return self.live_server_url + path

    def on_path(self, path):
        """Checks if the driver's current URL matches a given path."""
        return self.driver.current_url == self.path(path)

    def in_page_source(self, search_string):
        """Checks if a string is present anywhere inside the entire current page."""
        return search_string in self.driver.page_source

    def check_page_available(self, path, expected_text):
        """Checks if a page on a given path is available by matching against its title."""
        url = self.live_server_url + path
        self.driver.get(url)

        self.wait.until(EC.url_to_be(self.path(path)))

        return expected_text in self.driver.title

    def check_page_link(self, href, link_id, expected_url):
        """Checks if the link to a page works by confirming that the driver is on it."""

        driver = self.driver
        url = self.live_server_url + href

        driver.get(url)

        link = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, link_id))
        )
        link.click()

        self.wait.until(EC.url_to_be(expected_url))

        return expected_url in driver.current_url

    def fill_signup_form(self, username, email, password):
        driver = self.driver

        self.wait.until(EC.presence_of_element_located((By.NAME, "username")))

        driver.find_element(By.NAME, "username").send_keys(username)
        driver.find_element(By.NAME, "email").send_keys(email)
        driver.find_element(By.NAME, "password1").send_keys(password)
        driver.find_element(By.NAME, "password2").send_keys(password)
        driver.find_element(By.ID, "signup_form_submit").click()

        self.wait.until_not(EC.presence_of_element_located((By.NAME, "username")))

    def fill_login_form(self, email, password):
        driver = self.driver

        self.wait.until(EC.presence_of_element_located((By.NAME, "username")))

        # again I know this looks weird, but the username field just points to the email field in terms of user authentication
        driver.find_element(By.NAME, "username").send_keys(email)
        driver.find_element(By.NAME, "password").send_keys(password)
        driver.find_element(By.ID, "login_form_submit").click()

        self.wait.until_not(EC.presence_of_element_located((By.NAME, "username")))


@override_settings(EMAIL_AUTHENTICATION=False)
class BaseLoggedInSeleniumTest(BaseSeleniumTest):
    """
    A base test type that automatically logs in the user upon setup,
    intended to test pages that are only accessible to logged-in users.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        """
        Implement this in your derived class if you want extra startup
        functionality.
        """

        self.user = Users.create_user(**TEST_USER_CREDENTIALS)

        self.cat1 = Category.objects.create(
            user=self.user,
            name="tabby",
            description="stripes",
            entry_type=EntryType.INCOME,
        )

        self.cat2 = Category.objects.create(
            user=self.user,
            name="tuxedo",
            description=":3",
            entry_type=EntryType.EXPENSE,
        )

        self.ent1 = Entry.objects.create(
            date="2025-01-02",
            user=self.user,
            name="the first",
            description="foo",
            entry_type=EntryType.INCOME,
            category=self.cat1,
            amount=50,
        )

        self.ent2 = Entry.objects.create(
            date="2025-02-03",
            user=self.user,
            name="the second",
            description="bar",
            entry_type=EntryType.EXPENSE,
            category=self.cat2,
            amount=40,
        )

        self.ent3 = Entry.objects.create(
            date="2025-03-04",
            user=self.user,
            name="the third",
            description="baz",
            entry_type=EntryType.INCOME,
            category=self.cat1,
            amount=35,
        )

        # expected values:
        #   income total: 85
        #   expense total: 40
        #   net total: 45

        self.driver.get(self.path("/accounts/login"))
        self.fill_login_form(
            TEST_USER_CREDENTIALS["email"], TEST_USER_CREDENTIALS["password"]
        )


class TestGuestPages(BaseSeleniumTest):
    """Test for access to pages that do not require an account to access."""

    def test_home_page_available(self):
        assert self.check_page_available("/", "Welcome to Finance Tracker")

    def test_signup_page_available(self):
        assert self.check_page_available("/accounts/signup/", "Sign Up")

    def test_login_page_available(self):
        assert self.check_page_available("/accounts/login/", "Log In")


class TestUserWithAuth(BaseSeleniumTest):
    """Test that signup and login with email auth works."""

    def fill_auth_form(self):
        self.wait.until(EC.presence_of_element_located((By.NAME, "code")))

        auth_code = AuthSession.objects.get(
            user__username=TEST_USER_CREDENTIALS["username"]
        ).code

        assert self.driver.find_element(By.NAME, "code")

        self.driver.find_element(By.NAME, "code").send_keys(auth_code)
        self.driver.find_element(By.ID, "signup_form_submit").click()

        self.wait.until(EC.url_contains("/finances/dashboard/"))

        assert self.on_path("/finances/dashboard/")

    def test_signup_auth(self):
        self.driver.get(self.path("/accounts/signup"))
        self.fill_signup_form(**TEST_USER_CREDENTIALS)
        self.fill_auth_form()

    def test_login_auth(self):
        Users.create_user(**TEST_USER_CREDENTIALS)

        self.driver.get(self.path("/accounts/login"))
        self.fill_login_form(
            TEST_USER_CREDENTIALS["email"], TEST_USER_CREDENTIALS["password"]
        )
        self.fill_auth_form()

    def test_logout(self):
        Users.create_user(**TEST_USER_CREDENTIALS)

        self.driver.get(self.path("/accounts/login"))
        self.fill_login_form(
            TEST_USER_CREDENTIALS["email"], TEST_USER_CREDENTIALS["password"]
        )
        self.fill_auth_form()

        self.driver.find_element(By.ID, "logout_submit").click()
        self.wait.until(EC.url_changes(self.path("/finances/dashboard/")))

        assert self.on_path("/")


class TestDashboard(BaseLoggedInSeleniumTest):
    def test_dashboard_available(self):
        assert self.check_page_available("/finances/dashboard/", "Dashboard")
        assert self.in_page_source(
            f"Welcome to your Dashboard, {TEST_USER_CREDENTIALS['username']}!"
        )

    def test_balance_calculator(self):
        self.wait.until(EC.presence_of_element_located((By.ID, "calculate-button")))
        self.driver.find_element(By.ID, "calculate-button").click()

        income_selector = (By.ID, "income-total-display")
        expense_selector = (By.ID, "expense-total-display")
        net_selector = (By.ID, "net-total-display")

        self.wait.until_not(EC.text_to_be_present_in_element(income_selector, "$0.00"))
        self.wait.until_not(EC.text_to_be_present_in_element(expense_selector, "$0.00"))
        self.wait.until_not(EC.text_to_be_present_in_element(net_selector, "$0.00"))

        assert self.driver.find_element(*income_selector).text == "$85.00"
        assert self.driver.find_element(*expense_selector).text == "$40.00"
        assert self.driver.find_element(*net_selector).text == "$45.00"

    def test_latest_transactions_display(self):
        assert self.in_page_source("the first")
        assert self.in_page_source("foo")
        assert self.in_page_source("the second")
        assert self.in_page_source("bar")
        assert self.in_page_source("the third")
        assert self.in_page_source("baz")


class TestTransactions(BaseLoggedInSeleniumTest):
    def fill_transaction_form(
        self, add, date, name, amount, entry_type_income, category, description
    ):
        self.wait.until(EC.presence_of_element_located((By.NAME, "date")))
        original_date_element = self.driver.find_element(By.NAME, "date")

        # TODO: make this into a method that only applies present arguments
        if not add:
            Select(self.driver.find_element(By.NAME, "category")).select_by_index(0)
            self.driver.find_element(By.NAME, "description").clear()

            self.driver.find_element(By.NAME, "name").clear()
            self.driver.find_element(By.NAME, "amount").clear()

        original_date_element.send_keys(date)
        self.driver.find_element(By.NAME, "name").send_keys(name)
        self.driver.find_element(By.NAME, "amount").send_keys(amount)
        if entry_type_income:
            self.driver.find_element(By.ID, "transaction-type_0").click()
        else:
            self.driver.find_element(By.ID, "transaction-type_1").click()
        Select(self.driver.find_element(By.NAME, "category")).select_by_visible_text(
            category
        )
        self.driver.find_element(By.NAME, "description").send_keys(description)

        if add:
            self.select_btn_by_text("Add").click()
        else:
            self.select_btn_by_text("Apply").click()

        self.wait.until(EC.staleness_of(original_date_element))

    def select_btn_by_text(self, text):
        return self.driver.find_element(By.XPATH, f"//button[text()='{text}']")

    def select_entry_by_name(self, name):
        return self.driver.find_element(By.XPATH, f"//td[text()='{name}']")

    def test_transactions_available(self):
        assert self.check_page_available("/finances/transactions/", "Transactions")
        assert self.in_page_source("All-Time Net Transactions")
        assert self.in_page_source("$45.00")

    def test_transactions_add(self):
        self.driver.get(self.path("/finances/transactions/"))

        new_entry = {
            "date": "04/05/2025",
            "name": "the fourth",
            "amount": "7.50",
            "entry_type_income": False,
            "category": self.cat2.name,
            "description": "qux",
        }

        self.fill_transaction_form(add=True, **new_entry)

        assert self.in_page_source("$37.50")

        rows = self.driver.find_elements(By.CLASS_NAME, "entry")
        assert len(rows) == 4

    def test_transactions_delete(self):
        self.driver.get(self.path("/finances/transactions/"))
        self.wait.until(EC.presence_of_element_located((By.NAME, "date")))

        original_row = self.select_entry_by_name(self.ent1.name)

        self.select_entry_by_name(self.ent3.name).click()
        self.driver.find_element(By.ID, "trans-delete").click()
        self.wait.until(EC.alert_is_present())
        self.driver.switch_to.alert.accept()

        self.wait.until(EC.staleness_of(original_row))

        assert self.in_page_source("$10.00")

        rows = self.driver.find_elements(By.CLASS_NAME, "entry")
        assert len(rows) == 2

    def test_transactions_edit(self):
        self.driver.get(self.path("/finances/transactions/"))
        self.wait.until(EC.presence_of_element_located((By.NAME, "date")))

        self.select_entry_by_name(self.ent2.name).click()
        self.driver.find_element(By.ID, "trans-edit").click()
        self.wait.until(lambda driver: "Editing Transaction" in driver.page_source)

        entry = {
            "date": "04/05/2025",
            "name": "the fourth",
            "amount": "9.99",
            "entry_type_income": False,
            "category": self.cat2.name,
            "description": "qux (updated)",
        }

        self.fill_transaction_form(add=False, **entry)
        self.wait.until(lambda driver: "Add Transaction" in driver.page_source)

        assert self.in_page_source("$75.01")
        assert self.in_page_source("qux (updated)")

    def test_transactions_filter(self):
        # For now this only tests the date range
        self.driver.get(self.path("/finances/transactions/"))
        self.wait.until(EC.presence_of_element_located((By.NAME, "date")))
        original_date_element = self.driver.find_element(By.NAME, "date")

        self.driver.find_element(By.NAME, "date_end").send_keys("02/01/2025")
        self.select_btn_by_text("Apply Filters").click()

        self.wait.until(EC.staleness_of(original_date_element))

        rows = self.driver.find_elements(By.CLASS_NAME, "entry")
        assert len(rows) == 1

        assert self.in_page_source("the first")
        assert not self.in_page_source("the second")


class TestReports(BaseLoggedInSeleniumTest):
    def go_to_reports(self):
        self.driver.get(self.path("/finances/reports/"))
        self.wait.until(EC.presence_of_element_located((By.ID, "acct-report-title")))

    def test_reports_available(self):
        assert self.check_page_available("/finances/reports/", "Reports")
        assert self.in_page_source("All Transaction Data")
        assert self.in_page_source("Category Transaction Data")
        assert self.in_page_source("Net Savings")
        assert self.in_page_source("Expenses By Category")
        assert self.in_page_source("Income By Category")

    def test_account_report_change_period(self):
        self.go_to_reports()

        Select(self.driver.find_element(By.NAME, "acct-period")).select_by_value("year")
        self.driver.find_element(By.NAME, "acct_submit").click()

        self.wait.until(
            EC.text_to_be_present_in_element(
                (By.ID, "acct-report-title"), "The Last Year"
            )
        )

        title = self.driver.find_element(By.ID, "acct-report-title").text
        assert "The Last Year" in title

    def test_category_report_change_period_and_category(self):
        self.go_to_reports()

        Select(
            self.driver.find_element(By.NAME, "cat-category")
        ).select_by_visible_text(self.cat2.name)
        Select(self.driver.find_element(By.NAME, "cat-period")).select_by_value("week")
        self.driver.find_element(By.NAME, "cat_submit").click()

        self.wait.until(
            EC.text_to_be_present_in_element(
                (By.ID, "cat-report-title"), "The Last Week"
            )
        )

        title = self.driver.find_element(By.ID, "cat-report-title").text
        assert "The Last Week" in title

    def test_savings_report_change_period(self):
        self.go_to_reports()

        Select(self.driver.find_element(By.NAME, "savings-period")).select_by_value(
            "week"
        )
        self.driver.find_element(By.NAME, "savings_submit").click()

        self.wait.until(
            EC.text_to_be_present_in_element(
                (By.ID, "savings-report-title"), "The Last Week"
            )
        )

        title = self.driver.find_element(By.ID, "savings-report-title").text
        assert "The Last Week" in title

    def test_pie_reports_have_json_data(self):
        self.go_to_reports()

        self.wait.until(EC.presence_of_element_located((By.ID, "exp-pie-data")))

        exp_script = self.driver.find_element(By.ID, "exp-pie-data")
        inc_script = self.driver.find_element(By.ID, "inc-pie-data")

        assert exp_script.get_attribute("type") == "application/json"
        assert inc_script.get_attribute("type") == "application/json"
        assert exp_script.get_attribute("textContent").strip() != ""
        assert inc_script.get_attribute("textContent").strip() != ""


class TestCategories(BaseLoggedInSeleniumTest):
    def get_category_card(self, name):
        cards = self.driver.find_elements(By.CLASS_NAME, "category-card")
        for card in cards:
            if name in card.text:
                return card
        raise AssertionError(f"Category card with name '{name}' not found")

    def test_categories_available(self):
        assert self.check_page_available("/finances/categories/", "Categories")
        assert self.in_page_source("Your Categories")

    def test_categories_add(self):
        self.driver.get(self.path("/finances/categories/"))

        self.driver.find_element(By.ID, "new-category-button").click()
        self.wait.until(EC.visibility_of_element_located((By.ID, "category-popup")))

        self.driver.find_element(By.ID, "category-name").send_keys("Selenium Cat")
        Select(self.driver.find_element(By.ID, "category-type")).select_by_value(
            "EXPENSE"
        )

        self.driver.find_element(By.ID, "save-button").click()

        self.wait.until(EC.invisibility_of_element_located((By.ID, "category-popup")))

        assert self.in_page_source("Selenium Cat")

    def test_categories_edit(self):
        self.driver.get(self.path("/finances/categories/"))

        old_name = self.cat2.name

        card = self.get_category_card(old_name)
        card.find_element(By.CLASS_NAME, "edit-button").click()

        self.wait.until(EC.visibility_of_element_located((By.ID, "category-popup")))

        name_input = self.driver.find_element(By.ID, "category-name")
        assert name_input.get_attribute("value") == old_name

        new_name = "tuxedo updated"
        name_input.clear()
        name_input.send_keys(new_name)

        self.driver.find_element(By.ID, "save-button").click()

        self.wait.until(EC.invisibility_of_element_located((By.ID, "category-popup")))

        # Collect category names from the cards
        cards = self.driver.find_elements(By.CLASS_NAME, "category-card")
        names = [c.find_element(By.CLASS_NAME, "category-name").text for c in cards]

        assert new_name in names
        assert old_name not in names

    def test_categories_delete(self):
        self.driver.get(self.path("/finances/categories/"))

        name = self.cat1.name
        card = self.get_category_card(name)
        card.find_element(By.CLASS_NAME, "delete-button").click()

        # Handle confirmation alert
        self.wait.until(EC.alert_is_present())
        alert = self.driver.switch_to.alert
        assert "Are you sure you want to delete this category?" in alert.text
        alert.accept()

        # Wait until the category name is gone from the DOM
        self.wait.until(lambda driver: name not in driver.page_source)

        assert name not in self.driver.page_source

    def test_view_transactions_link_navigates(self):
        self.driver.get(self.path("/finances/categories/"))

        card = self.get_category_card(self.cat2.name)
        card.find_element(By.CLASS_NAME, "view-transactions").click()

        self.wait.until(lambda driver: "/finances/transactions" in driver.current_url)

        assert "/finances/transactions/" in self.driver.current_url
        assert self.in_page_source("All-Time Net Transactions")


class TestGoals(BaseLoggedInSeleniumTest):
    def go_to_goals(self):
        self.driver.get(self.path("/finances/goals/"))
        self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".acct-goal-section h1"))
        )

    def get_acct_goal_row(self, name):
        rows = self.driver.find_elements(By.CSS_SELECTOR, ".acct-goal-row")
        for row in rows:
            if name in row.text:
                return row
        raise AssertionError(f"Account goal row with name '{name}' not found")

    def get_cat_goal_row(self, name):
        rows = self.driver.find_elements(By.CSS_SELECTOR, ".cat-goal-row")
        for row in rows:
            if name in row.text:
                return row
        raise AssertionError(f"Category goal row with name '{name}' not found")

    def test_goals_available(self):
        assert self.check_page_available("/finances/goals/", "Goals")
        assert self.in_page_source("Account Goals")
        assert self.in_page_source("Category Goals")

    def test_add_account_goal(self):
        self.go_to_goals()

        self.driver.find_element(By.ID, "acct-goal-add-btn").click()
        dialog = self.wait.until(
            EC.visibility_of_element_located((By.ID, "acct-goal-add-dialog"))
        )

        dialog.find_element(By.NAME, "name").send_keys("Selenium Account Goal")
        # entry_type exists on AddAccountGoalForm
        Select(dialog.find_element(By.NAME, "entry_type")).select_by_value("EXPENSE")
        # time_length controls start/end on the backend
        Select(dialog.find_element(By.NAME, "time_length")).select_by_value("monthly")

        amount_input = dialog.find_element(By.NAME, "amount")
        amount_input.clear()
        amount_input.send_keys("500.00")

        dialog.find_element(By.ID, "acct-goal-add-submit").click()

        self.wait.until(lambda driver: "Selenium Account Goal" in driver.page_source)
        row = self.get_acct_goal_row("Selenium Account Goal")
        assert row is not None

    def test_add_category_goal(self):
        self.go_to_goals()

        self.driver.find_element(By.ID, "category-goals-add").click()
        dialog = self.wait.until(
            EC.visibility_of_element_located((By.ID, "cat-goal-add-dialog"))
        )

        # Make sure category field exists on AddCategoryGoalForm
        Select(dialog.find_element(By.NAME, "category")).select_by_visible_text(
            self.cat2.name
        )
        dialog.find_element(By.NAME, "name").send_keys("Selenium Category Goal")
        Select(dialog.find_element(By.NAME, "time_length")).select_by_value("monthly")

        amount_input = dialog.find_element(By.NAME, "amount")
        amount_input.clear()
        amount_input.send_keys("100.00")

        dialog.find_element(By.ID, "cat-goal-add-submit").click()

        self.wait.until(lambda driver: "Selenium Category Goal" in driver.page_source)
        row = self.get_cat_goal_row("Selenium Category Goal")
        assert row is not None

    def test_category_filter_shows_only_selected(self):
        self.go_to_goals()

        # Make sure at least one goal exists for cat2
        if "Selenium Category Goal" not in self.driver.page_source:
            self.driver.find_element(By.ID, "category-goals-add").click()
            dialog = self.wait.until(
                EC.visibility_of_element_located((By.ID, "cat-goal-add-dialog"))
            )

            Select(dialog.find_element(By.NAME, "category")).select_by_visible_text(
                self.cat2.name
            )
            dialog.find_element(By.NAME, "name").send_keys("Selenium Category Goal")
            Select(dialog.find_element(By.NAME, "time_length")).select_by_value(
                "monthly"
            )

            amount_input = dialog.find_element(By.NAME, "amount")
            amount_input.clear()
            amount_input.send_keys("100.00")

            dialog.find_element(By.ID, "cat-goal-add-submit").click()
            self.wait.until(
                lambda driver: "Selenium Category Goal" in driver.page_source
            )

        # Use the category filter dropdown
        Select(self.driver.find_element(By.ID, "category-filter")).select_by_value(
            str(self.cat2.id)
        )

        def only_cat2_visible(driver):
            rows = driver.find_elements(By.CSS_SELECTOR, ".cat-goal-row")
            any_visible = False
            for row in rows:
                if row.is_displayed():
                    any_visible = True
                    if row.get_attribute("data-category-id") != str(self.cat2.id):
                        return False
            return any_visible

        self.wait.until(only_cat2_visible)

        rows = self.driver.find_elements(By.CSS_SELECTOR, ".cat-goal-row")
        for row in rows:
            if row.is_displayed():
                assert row.get_attribute("data-category-id") == str(self.cat2.id)

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
    def test_reports_available(self):
        assert self.check_page_available("/finances/reports/", "Reports")
        assert self.in_page_source("All Transaction Data")


class TestCategories(BaseLoggedInSeleniumTest):
    def test_categories_available(self):
        assert self.check_page_available("/finances/categories/", "Categories")
        assert self.in_page_source("Your Categories")


class TestGoals(BaseLoggedInSeleniumTest):
    def test_goals_available(self):
        assert self.check_page_available("/finances/goals/", "Goals")
        assert self.in_page_source("Account Goals")
        assert self.in_page_source("Category Goals")


"""
# Tests for the home page (so far this is just links to other pages)
class NavAndHomePage(BaseSeleniumTest):
    def test_nav_home_link(self):
        self.check_page_link("/", "nav-home", "/")

    def test_home_signup_link_2(self):
        self.check_page_link("/", "page-signup-link", "/accounts/signup/")

    def test_home_login_link_2(self):
        self.check_page_link("/", "page-login-link", "/accounts/login/")

    # Creates testuser to login and access the dashboard
    def test_nav_dashboard_link(self):
        self.setUpTestData()
        self.driver.get(self.live_server_url + "/accounts/login")
        self.fill_login_form(self.email, self.password)
        self.wait.until(EC.url_contains("/dashboard/"))
        self.check_page_link("/dashboard/", "nav-dashboard", "/dashboard/")
        self.check_page_link("/", "nav-dashboard", "/dashboard/")

    # Creates testuser to login and then logout
    def test_nav_logout(self):
        self.setUpTestData()
        self.driver.get(self.live_server_url + "/accounts/login")
        self.fill_login_form(self.username, self.password)
        self.wait.until(EC.url_contains("/dashboard/"))
        self.driver.find_element(By.ID, "logout_submit").click()
        assert self.driver.current_url == self.live_server_url + "/"


# Tests for the signup page
class SignupPage(BaseSeleniumTest):
    # Test the login link on the page
    def test_login_link(self):
        self.check_page_link("/accounts/signup", "page-login-link", "/accounts/login/")

    # Helper method to fill the signup form given inputs
    def fill_signup_form(self, username, pw1, pw2):
        driver = self.driver
        driver.find_element(By.NAME, "username").send_keys(username)
        driver.find_element(By.NAME, "password1").send_keys(pw1)
        driver.find_element(By.NAME, "password2").send_keys(pw2)
        driver.find_element(By.ID, "signup_form_submit").click()

    # Tests to see if a user can sign in with valid inputs
    def test_user_can_signup(self):
        driver = self.driver
        driver.get(self.live_server_url + "/accounts/signup/")

        username = "testuser"
        pass1 = "testPass1234"
        pass2 = "testPass1234"

        self.fill_signup_form(username, pass1, pass2)

        self.wait.until(EC.url_contains("/dashboard/"))

        time.sleep(2)

        assert f"Welcome, {username}!" in driver.page_source

# Tests for the login page
class LoginPage(BaseSeleniumTest):
    def test_signup_link(self):
        self.check_page_link(
            "/accounts/login/", "page-signup-link", "/accounts/signup/"
        )

"""

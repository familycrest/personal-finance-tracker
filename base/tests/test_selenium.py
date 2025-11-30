from django.test import override_settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth import get_user_model

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions

# from webdriver_manager.core.os_manager import ChromeType
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

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
        return self.live_server_url + path

    def on_path(self, path):
        return self.driver.current_url == self.path(path)

    def in_page_source(self, search_string):
        assert search_string in self.driver.page_source

    # Checks to see if user can access a page
    def check_page_available(self, path, expected_text):
        url = self.live_server_url + path
        self.driver.get(url)

        self.wait.until(EC.url_to_be(self.path(path)))

        assert expected_text in self.driver.title

    # Checks to see if a link from a given page to a different page is functional
    def check_page_link(self, href, link_id, expected_url):
        driver = self.driver
        url = self.live_server_url + href

        driver.get(url)

        # time.sleep(2)

        link = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, link_id))
        )
        link.click()

        # time.sleep(2)

        assert expected_url in driver.current_url

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


class TestGuestPages(BaseSeleniumTest):
    """Test for access to pages that do not require an account to access."""

    def test_home_page_available(self):
        self.check_page_available("/", "Welcome to Finance Tracker")

    def test_signup_page_available(self):
        self.check_page_available("/accounts/signup/", "Sign Up")

    def test_login_page_available(self):
        self.check_page_available("/accounts/login/", "Log In")


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


@override_settings(EMAIL_AUTHENTICATION=False)
class BaseLoggedInSeleniumTest(BaseSeleniumTest):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
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


class TestDashboard(BaseLoggedInSeleniumTest):
    def test_dashboard_available(self):
        self.check_page_available("/finances/dashboard/", "Dashboard")
        self.in_page_source(
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
        self.in_page_source("the first")
        self.in_page_source("foo")
        self.in_page_source("the second")
        self.in_page_source("bar")
        self.in_page_source("the third")
        self.in_page_source("baz")


class TestTransactions(BaseLoggedInSeleniumTest):
    def test_transactions_available(self):
        self.check_page_available("/finances/transactions/", "Transactions")
        self.in_page_source("All-Time Net Transactions")
        self.in_page_source("$45.00")


class TestReports(BaseLoggedInSeleniumTest):
    def test_reports_available(self):
        self.check_page_available("/finances/reports/", "Reports")
        self.in_page_source("All Transaction Data")


class TestCategories(BaseLoggedInSeleniumTest):
    def test_categories_available(self):
        self.check_page_available("/finances/categories/", "Categories")
        self.in_page_source("Your Categories")


class TestGoals(BaseLoggedInSeleniumTest):
    def test_goals_available(self):
        self.check_page_available("/finances/goals/", "Goals")
        self.in_page_source("Account Goals")
        self.in_page_source("Category Goals")


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

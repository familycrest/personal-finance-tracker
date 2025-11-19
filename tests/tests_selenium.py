from django.test import LiveServerTestCase
from django.contrib.auth import get_user_model

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions

# from webdriver_manager.core.os_manager import ChromeType
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time

# from webdriver_manager.microsoft import EdgeChromiumDriverManager
# from selenium.webdriver.edge.service import Service as EdgeService
# from selenium.webdriver.edge.options import Options as EdgeOptions

# from webdriver_manager.firefox import GeckoDriverManager
# from selenium.webdriver.firefox.service import Service as FirefoxService
# from selenium.webdriver.firefox.options import Options as FirefoxOptions


# Contains driver setup/teardown methods and common methods that could be used in several classes
class BaseSeleniumTest(LiveServerTestCase):
    # Driver setup
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        chrome_options = ChromeOptions()
        # Comment/uncomment the line below to toggle headless testing
        # chrome_options.add_argument("--headless")

        cls.driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()),
            options=chrome_options,
        )
        cls.wait = WebDriverWait(cls.driver, 5)

    # Driver teardown
    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()

    def setUpTestData(obj):
        obj.test_username = "testuser"
        obj.test_password = "testPass1234"
        get_user_model().objects.create_user(
            username=obj.test_username, password=obj.test_password
        )

    # Checks to see if user can access a page
    def check_page_available(self, path, expected_text):
        url = self.live_server_url + path
        self.driver.get(url)

        time.sleep(2)

        self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        assert expected_text in self.driver.title

    # Checks to see if a link from a given page to a different page is functional
    def check_page_link(self, href, link_id, expected_url):
        driver = self.driver
        url = self.live_server_url + href

        driver.get(url)

        time.sleep(2)

        link = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, link_id))
        )
        link.click()

        time.sleep(2)

        assert expected_url in driver.current_url

    def fill_login_form(self, username, password):
        driver = self.driver

        self.wait.until(EC.presence_of_element_located((By.NAME, "username")))

        driver.find_element(By.NAME, "username").send_keys(username)
        driver.find_element(By.NAME, "password").send_keys(password)
        driver.find_element(By.ID, "login_form_submit").click()


# Tests for access to pages that do not require a logged in user
class TestNoUserPagesAvailable(BaseSeleniumTest):
    def test_home_page_availability(self):
        self.check_page_available("/", "Welcome to Finance Tracker")

    def test_signup_page_availability(self):
        self.check_page_available("/accounts/signup/", "Sign Up")

    def test_login_page_availability(self):
        self.check_page_available("/accounts/login/", "Log In")


# class TestUserPagesAvailable(BaseSeleniumTest):


# Tests for the home page (so far this is just links to other pages)
class TestNavAndHomePage(BaseSeleniumTest):
    def test_nav_home_link(self):
        self.check_page_link("/", "nav-home", "/")

    def test_nav_signup_link(self):
        self.check_page_link("/", "nav-signup", "/accounts/signup/")

    def test_nav_login_link(self):
        self.check_page_link("/", "nav-login", "/accounts/login/")

    def test_home_signup_link_2(self):
        self.check_page_link("/", "page-signup-link", "/accounts/signup/")

    def test_home_login_link_2(self):
        self.check_page_link("/", "page-login-link", "/accounts/login/")

    # Creates testuser to login and access the dashboard
    def test_nav_dashboard_link(self):
        self.setUpTestData()
        self.driver.get(self.live_server_url + "/accounts/login")
        self.fill_login_form(self.test_username, self.test_password)
        self.wait.until(EC.url_contains("/dashboard/"))
        self.check_page_link("/dashboard/", "nav-dashboard", "/dashboard/")
        self.check_page_link("/", "nav-dashboard", "/dashboard/")

    # Creates testuser to login and then logout
    def test_nav_logout(self):
        self.setUpTestData()
        self.driver.get(self.live_server_url + "/accounts/login")
        self.fill_login_form(self.test_username, self.test_password)
        time.sleep(2)
        self.wait.until(EC.url_contains("/dashboard/"))
        self.driver.find_element(By.ID, "logout_submit").click()
        time.sleep(2)
        assert self.driver.current_url == self.live_server_url + "/"


# Tests for the signup page
class SignupPageTest(BaseSeleniumTest):
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

    # Negative tests for signup
    # User gives no input
    def test_failed_signup_given_no_inputs(self):
        driver = self.driver
        driver.get(self.live_server_url + "/accounts/signup/")

        driver.find_element(By.ID, "signup_form_submit").click()

        username_field = driver.find_element(By.NAME, "username")
        time.sleep(2)

        assert username_field.get_attribute("required") == "true"
        assert username_field.get_attribute("validationMessage") != ""

    # User gives no username, but inputs passwords
    def test_failed_signup_given_no_username(self):
        driver = self.driver
        driver.get(self.live_server_url + "/accounts/signup/")

        pass1 = "testPass1234"
        pass2 = "testPass1234"
        self.fill_signup_form("", pass1, pass2)

        username_field = driver.find_element(By.NAME, "username")
        time.sleep(2)

        assert username_field.get_attribute("required") == "true"
        assert username_field.get_attribute("validationMessage") != ""

    # User gives a username, but no passwords
    def test_failed_signup_given_no_passwords(self):
        driver = self.driver
        driver.get(self.live_server_url + "/accounts/signup/")

        username = "testuser"
        self.fill_signup_form(username, "", "")

        password1_field = driver.find_element(By.NAME, "password1")
        time.sleep(2)

        assert password1_field.get_attribute("required")
        assert password1_field.get_attribute("validationMessage") != ""

    # User gives a username and password, but no password confirmation
    def test_failed_signup_given_no_password_confirmation(self):
        driver = self.driver
        driver.get(self.live_server_url + "/accounts/signup/")

        username = "testuser"
        pass1 = "testPass1234"
        self.fill_signup_form(username, pass1, "")

        password2_field = driver.find_element(By.NAME, "password2")
        time.sleep(2)

        assert password2_field.get_attribute("required")
        assert password2_field.get_attribute("validationMessage") != ""

    def test_failed_signup_all_user_data_already_exists(self):
        driver = self.driver
        driver.get(self.live_server_url + "/accounts/signup/")
        self.setUpTestData()

        username = "testuser"
        pass1 = "testPass12345"
        pass2 = "testPass12345"
        self.fill_signup_form(username, pass1, pass2)

        error_field = self.wait.until(
            EC.presence_of_element_located((By.ID, "id_username_error"))
        )

        time.sleep(2)

        assert "A user with that username already exists." in error_field.text

    def test_failed_signup_username_already_exists(self):
        driver = self.driver
        driver.get(self.live_server_url + "/accounts/signup/")
        self.setUpTestData()

        username = "testuser"
        pass1 = "testPass1234"
        pass2 = "testPass1234"
        self.fill_signup_form(username, pass1, pass2)

        error_field = self.wait.until(
            EC.presence_of_element_located((By.ID, "id_username_error"))
        )

        time.sleep(2)

        assert "A user with that username already exists." in error_field.text

    # def test_failed_signup_password_already_exists(self):
    #     driver = self.driver
    #     driver.get(self.live_server_url + "/accounts/signup/")
    #     self.setUpTestData()

    #     username = "testuser2"
    #     pass1 = "testPass1234"
    #     pass2 = "testPass1234"
    #     self.fill_signup_form(username, pass1, pass2)

    #     error_field = self.wait.until(
    #         EC.presence_of_element_located((By.ID, "id_password_error"))
    #     )

    #     time.sleep(2)

    #     assert "A user with that password already exists." in error_field.text


# Tests for the login page
class LoginPageTest(BaseSeleniumTest):
    def test_signup_link(self):
        self.check_page_link(
            "/accounts/login/", "page-signup-link", "/accounts/signup/"
        )

    def test_user_can_login(self):
        driver = self.driver
        driver.get(self.live_server_url + "/accounts/login/")

        self.setUpTestData()

        self.fill_login_form(self.test_username, self.test_password)

        self.wait.until(EC.url_contains("/dashboard/"))

        time.sleep(2)

        assert f"Welcome, {self.test_username}!" in driver.page_source

    # Negative tests for login
    # User gives no inputs
    def test_failed_login_given_no_inputs(self):
        driver = self.driver
        driver.get(self.live_server_url + "/accounts/login/")

        self.setUpTestData()
        self.fill_login_form("", "")

        username_field = driver.find_element(By.NAME, "username")
        time.sleep(2)

        assert username_field.get_attribute("required") == "true"
        assert username_field.get_attribute("validationMessage") != ""

    # User gives password, but no username
    def test_failed_login_given_no_username(self):
        driver = self.driver
        driver.get(self.live_server_url + "/accounts/login/")

        self.setUpTestData()
        self.fill_login_form("", self.test_password)

        username_field = driver.find_element(By.NAME, "username")
        time.sleep(2)

        assert username_field.get_attribute("required") == "true"
        assert username_field.get_attribute("validationMessage") != ""

    # User gives username, but no password
    def test_failed_login_given_no_password(self):
        driver = self.driver
        driver.get(self.live_server_url + "/accounts/login/")

        self.setUpTestData()
        self.fill_login_form(self.test_username, "")

        password_field = driver.find_element(By.NAME, "password")
        time.sleep(2)

        assert password_field.get_attribute("required") == "true"
        assert password_field.get_attribute("validationMessage") != ""

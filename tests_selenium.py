from django.test import LiveServerTestCase
from django.contrib.auth.models import User

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.core.os_manager import ChromeType
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
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
        # Uncomment the line below for headless testing
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

    def setUpTestData(cls):
        cls.test_username = "testuser"
        cls.test_password = "testPass1234"
        User.objects.create_user(username=cls.test_username, password=cls.test_password)

    # Checks to see if user can access a page
    def check_page_available(self, path, expected_text):
        url = self.live_server_url + path
        self.driver.get(url)

        time.sleep(2)

        body = self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        assert expected_text in self.driver.title

    # Checks to see if a link from a given page to a different page is functional
    def check_page_link(self, href, link_id, expected_url):
        driver = self.driver
        url = self.live_server_url + href

        driver.get(url)

        time.sleep(2)

        link = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, f"{link_id}"))
        )
        link.click()

        time.sleep(2)

        assert expected_url in driver.current_url

    def fill_login_form(self, username, password):
        driver = self.driver

        input_available = self.wait.until(
            EC.presence_of_element_located((By.NAME, "username"))
        )

        driver.find_element(By.NAME, "username").send_keys(username)
        driver.find_element(By.NAME, "password").send_keys(password)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()


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

    def test_nav_dashboard_link(self):
        self.setUpTestData()
        self.driver.get(self.live_server_url + "/accounts/login")
        self.fill_login_form(self.test_username, self.test_password)
        self.wait.until(EC.url_contains("/dashboard/"))
        self.check_page_link("/dashboard/", "nav-dashboard", "/dashboard/")

    # def test_nav_logout(self):
    #     self.setUpTestData()
    #     self.driver.get(self.live_server_url + "/accounts/login")
    #     self.fill_login_form(self.test_username, self.test_password)
    #     time.sleep(2)
    #     self.wait.until(EC.url_contains("/dashboard/"))
    #     self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    #     time.sleep(2)
    #     assert "Logged Out" in self.driver.title


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
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

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

    # Need to add negative test cases


# Tests for the login page
class LoginPageTest(BaseSeleniumTest):

    def test_signup_link(self):
        self.check_page_link(
            "/accounts/login/", "page-signup-link", "/accounts/signup/"
        )

    # def fill_login_form(self, username, password):
    #     driver = self.driver
    #     driver.find_element(By.NAME, "username").send_keys(username)
    #     driver.find_element(By.NAME, "password").send_keys(password)
    #     driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    def test_user_can_login(self):
        driver = self.driver
        driver.get(self.live_server_url + "/accounts/login/")

        self.setUpTestData()

        # input_available = self.wait.until(
        #     EC.presence_of_element_located((By.NAME, "username"))
        # )

        self.fill_login_form(self.test_username, self.test_password)

        self.wait.until(EC.url_contains("/dashboard/"))

        time.sleep(2)

        assert f"Welcome, {self.test_username}!" in driver.page_source

    # Need to create negative tests


# def check_driver_vs_chrome_version(self):
#     str1 = self.driver.capabilities["browserVersion"]
#     str2 = self.driver.capabilities["chrome"]["chromedriverVersion"].split(" ")[0]
#     print(str1)
#     print(str2)
#     print(str1[0:2])
#     print(str2[0:2])
#     if str1[0:2] != str2[0:2]:
#         print(
#             "Incorrect chrome driver version installed, please go kick Colton and get him to actually fix it this time."
#         )

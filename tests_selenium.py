from django.test import LiveServerTestCase
from selenium import webdriver

from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.core.os_manager import ChromeType


from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions

from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time


class BaseSeleniumTest(LiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        chrome_options = ChromeOptions()
        # Uncomment the line below for headless testing.
        # chrome_options.add_argument("--headless")

        cls.driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()),
            options=chrome_options,
        )
        cls.wait = WebDriverWait(cls.driver, 5)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()

    def check_page_available(self, path, expected_text):
        url = self.live_server_url + path
        self.driver.get(url)

        time.sleep(2)

        body = self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        assert expected_text in self.driver.title

    def check_page_link(self, href, expected_url):
        driver = self.driver
        home_url = self.live_server_url

        driver.get(home_url)

        time.sleep(2)

        link = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, f"a[href='{href}']"))
        )
        link.click()

        time.sleep(2)

        assert expected_url in driver.current_url


class TestNoUserPagesAvailable(BaseSeleniumTest):
    def test_home_page_availability(self):
        self.check_page_available("/", "Welcome to Finance Tracker")

    def test_signup_page_availability(self):
        self.check_page_available("/accounts/signup/", "Sign Up")

    def test_login_page_availability(self):
        self.check_page_available("/accounts/login/", "Log In")


# class TestUserPagesAvailable(BaseSeleniumTest):


class TestHomePage(BaseSeleniumTest):
    def test_nav_home_link(self):
        self.check_page_link("/", "/")

    def test_nav_signup_link(self):
        self.check_page_link("/accounts/signup/", "/accounts/signup/")

    def test_nav_login_link(self):
        self.check_page_link("/accounts/login/", "/accounts/login")

    # def test_signup_link_2(self):

    # def test_login_link_2(self):


class SignUpFormTest(BaseSeleniumTest):

    def test_user_can_signup(self):

        driver = self.driver
        driver.get(self.live_server_url + "/accounts/signup/")

        username = self.wait.until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        user = "testuser"
        username.send_keys(user)

        password1 = driver.find_element(By.NAME, "password1")
        password1.send_keys("testPassword123")

        password2 = driver.find_element(By.NAME, "password2")
        password2.send_keys("testPassword123")

        time.sleep(2)

        password2.send_keys(Keys.RETURN)

        self.wait.until(EC.url_contains("/dashboard/"))

        time.sleep(2)

        assert f"Welcome, {user}!" in driver.page_source


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

from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time


class TestAllPagesAvailable(LiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        chrome_options = Options()
        # Uncomment the line below for headless testing.
        # chrome_options.add_argument("--headless")
        cls.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=chrome_options
        )
        cls.wait = WebDriverWait(cls.driver, 5)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.driver.quit()

    def check_driver_vs_chrome_version(self):
        str1 = self.driver.capabilities["browserVersion"]
        str2 = self.driver.capabilities["chrome"]["chromedriverVersion"].split(" ")[0]
        print(str1)
        print(str2)
        print(str1[0:2])
        print(str2[0:2])
        if str1[0:2] != str2[0:2]:
            print(
                "Incorrect chrome driver version installed, please go kick Colton and get him to actually fix it this time."
            )

    def check_page_available(self, path, expected_text):
        url = self.live_server_url + path
        self.driver.get(url)

        time.sleep(2)

        element = self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        assert expected_text in self.driver.title

    def test_home_page(self):
        self.check_page_available("/", "Welcome to Finance Tracker")

    def test_signup_page(self):
        self.check_page_available("/accounts/signup/", "Sign Up")

    def test_login_page(self):
        self.check_page_available("/accounts/login/", "Log In")

    # Test fails because user must be logged in to log out?
    # def test_logout_page(self):
    #     self.check_page_available("/accounts/logout/", "Logged Out")

    # Test fails because user must be logged in?
    # def test_dashboard_page(self):
    #     self.check_page_available("/dashboard/", "Dashboard")


# class LoginFormTest(LiveServerTestCase):

#     def test_form(self):
#         driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

#         driver.get(self.live_server_url + "/login/")

#         time.sleep(3)

#         user_name = driver.find_element(By.NAME, "username")
#         user_password = driver.find_element(By.NAME, "password")

#         time.sleep(3)

#         submit_button = driver.find_element(By.TAG_NAME, "button")

#         user_name.send_keys("admin")
#         user_password.send_keys("admin")

#         submit_button.send_keys(Keys.RETURN)

#         assert "admin" in driver.page_source


# class SignUpFormTest(LiveServerTestCase):

#     def test_form(self):
#         driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

#         driver.get(self.live_server_url + "/signup/")

#         time.sleep(3)

#         user_name = driver.find_element(By.NAME, "username")
#         user_password = driver.find_element(By.NAME, "password1")
#         confirm_password = driver.find_element(By.NAME, "password2")

#         time.sleep(3)

#         submit_button = driver.find_element(By.TAG_NAME, "button")

#         user_name.send_keys("admin")
#         user_password.send_keys("adminpass")
#         confirm_password.send_keys("adminpass")

#         submit_button.send_keys(Keys.RETURN)

#         current_url = driver.current_url
#         expected_url = self.live_server_url + "/dashboard/"

#         assert current_url == expected_url

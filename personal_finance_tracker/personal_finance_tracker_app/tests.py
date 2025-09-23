from django.test import TestCase

# Create your tests here.
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
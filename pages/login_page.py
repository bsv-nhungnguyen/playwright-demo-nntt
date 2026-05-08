from pages.base_page import BasePage


class LoginPage(BasePage):
    """Login page for Odaku Admin — used by root conftest.py and test_login.py."""

    def __init__(self, page):
        super().__init__(page)
        self.email_input = page.get_by_role("textbox", name="sample@example.com")
        self.password_input = page.get_by_role("textbox", name="半角英数記号8文字以上32文字まで")
        self.login_button = page.get_by_role("button", name="ログイン", exact=True)

    def input_email(self, email: str):
        self.email_input.click()
        self.email_input.fill(email)

    def input_password(self, password: str):
        self.password_input.click()
        self.password_input.fill(password)

    def click_login(self):
        self.login_button.click()

from pages.base_page import BasePage
from pages.login_page import LoginPage

def test_login_006(access_to_login_page):
    """Check if user can input text into username and password fields."""
    login_page = access_to_login_page
    login_page.input_email("nhungntt")
    login_page.input_password("xxxx")
    assert login_page.get_input_value(login_page.email_input) == "nhungntt"
    assert login_page.get_input_value(login_page.password_input) == "xxxx"

def test_login_007(access_to_login_page):
    """Check data display in field [email]."""
    login_page = access_to_login_page
    login_page.input_email("nhungntt")
    breakpoint()
    assert login_page.get_input_value(login_page.email_input) == "nhungntt"
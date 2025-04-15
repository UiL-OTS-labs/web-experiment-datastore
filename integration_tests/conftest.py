import pytest


@pytest.fixture
def as_admin(browser, admin_user, live_server):
    context = browser.new_context()
    page = context.new_page()
    page.goto(live_server.url + "/login")

    page.fill("#id_username", "admin")
    page.fill("#id_password", "password")
    page.locator("button").filter(has_text="Log in").click()
    yield page


@pytest.fixture
def as_user(browser, live_server):
    # TODO
    pass

from playwright.sync_api import expect


def test_server_up(page, live_server):
    """check that the server can start and that it returns a meaningful response"""
    page.goto(live_server.url)
    expect(page).to_have_title('Web-experiment datastore')


def test_admin_menu(as_admin):
    """check that the admin login works and the admin menu is visible"""
    page = as_admin
    expect(page.locator('.navbar')).to_contain_text('My Experiments')
    expect(page.locator('.navbar')).to_contain_text('Administration')

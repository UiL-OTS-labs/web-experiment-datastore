from datetime import date, datetime
import uuid
from django.template import defaultfilters
from playwright.sync_api import expect

from experiments.models import DataPoint, Experiment
from main.models import User


def test_server_up(page, live_server):
    """check that the server can start and that it returns a meaningful response"""
    page.goto(live_server.url)
    expect(page).to_have_title('Web-experiment datastore')


def test_admin_menu(as_admin):
    """check that the admin login works and the admin menu is visible"""
    page = as_admin
    expect(page.locator('.navbar')).to_contain_text('My Experiments')
    expect(page.locator('.navbar')).to_contain_text('Administration')



def test_data_points_added_chronologically(as_admin, admin_user, db, live_server):
   
    exp = Experiment.objects.create(access_id=uuid.uuid4()) 
    page = as_admin
    

    exp.users.add(admin_user)
   


    # Create DataPoints
    dp1 = DataPoint.objects.create(experiment=exp)
    dp2 = DataPoint.objects.create(experiment=exp)
    dp3 = DataPoint.objects.create(experiment=exp)
    """
    Test that DataPoints are stored in chronological order by 'date_added' timestamp.
    """
    page.goto(live_server.url+ '/experiments/1/')
    page.locator("th").nth(3).click()
    

    rows = page.locator("#DataTables_Table_0 tbody tr")
    rendered_dates = [
        rows.nth(i).locator("td").nth(3).inner_text() for i in range(rows.count())
    ]

    expected = sorted([dp1, dp2, dp3], key=lambda dp: dp.date_added)
    expected_dates = [defaultfilters.date(dp.date_added)+ ", " + defaultfilters.time(dp.date_added) for dp in expected]

    assert rendered_dates == expected_dates
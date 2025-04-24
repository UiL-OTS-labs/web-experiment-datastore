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
    """
    Test that DataPoints are stored in chronological order by 'date_added' timestamp.
    """
    exp = Experiment.objects.create(access_id=uuid.uuid4()) 
    page = as_admin
    

    exp.users.add(admin_user)
   
  

    # Create DataPoints
    dp1 = DataPoint.objects.create(experiment=exp)
    dp1.date_added = datetime(2023, 10, 3, 11, 35)
    dp1.save()
    dp2 = DataPoint.objects.create(experiment=exp)
    dp2.date_added = datetime(2024, 10, 3, 23, 23)
    dp2.save()
    dp3 = DataPoint.objects.create(experiment=exp)
    dp3.date_added = datetime(2024, 10, 11, 17, 21)
    dp3.save()
    dp4 = DataPoint.objects.create(experiment=exp) 
    dp4.date_added = datetime(2024, 10, 23, 1, 35)
    dp4.save()
    dp5 = DataPoint.objects.create(experiment=exp) 
    dp5.date_added = datetime(2024, 10, 23, 2, 35)
    dp5.save()
    dp6 = DataPoint.objects.create(experiment=exp) 
    dp6.date_added = datetime(2024, 10, 23, 11, 35)
    dp6.save()
    #Bug 85 replicate


    page.goto(f'{live_server.url}/experiments/{exp.id}/')
    page.locator("#DataTables_Table_0 th").nth(3).click()


    rows = page.locator("#DataTables_Table_0 tbody tr")
    rendered_dates = [
        rows.nth(i).locator("td").nth(3).inner_text() for i in range(rows.count())
    ]

    expected = sorted([dp1, dp2, dp3, dp4, dp5, dp6], key=lambda dp: dp.date_added, reverse=True) #Reverse because it started comparing ascending to the descending list
    expected_dates = [defaultfilters.date(dp.date_added)+ ", " + defaultfilters.time(dp.date_added) for dp in expected]

    assert rendered_dates == expected_dates
from Tests.test_app import test_split_time
from covid_data_handler import parse_csv_data
from covid_data_handler import process_covid_csv_data
from covid_data_handler import covid_API_request
from covid_data_handler import schedule_covid_updates
from covid_data_handler import repeat_scheduled_covid_update
from covid_data_handler import  process_covid_API_data
import json

def test_parse_csv_data():
    data = parse_csv_data('nation_2021-10-28.csv')
    assert len(data) == 639

def test_process_covid_csv_data():
    last7days_cases , current_hospital_cases , total_deaths = \
        process_covid_csv_data ( parse_csv_data (
            'nation_2021-10-28.csv' ) )
    assert last7days_cases == 240_299
    assert current_hospital_cases == 7_019
    assert total_deaths == 141_544

def test_covid_API_request():
    data = covid_API_request()
    assert isinstance(data, dict)

def test_schedule_covid_updates():
    schedule_covid_updates(update_interval=10, update_name='update test')

def test_repeat_scheduled_covid_update():
    repeat_scheduled_covid_update(update_interval=10,update_name="update test",scheduled_event=schedule_covid_updates)

def test_process_covid_API_data():
    with open('covid_test.json', 'r', encoding="UTF-8") as covid_file:
        covid_dict=json.loads(covid_file.read())
    last7days_cases , current_hospital_cases , total_deaths = process_covid_API_data(covid_dict)
    assert current_hospital_cases == 5829
    assert total_deaths == 145824
    assert last7days_cases == 245343

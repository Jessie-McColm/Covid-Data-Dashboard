'''
Handles all the updates to covid data from the covid API and handles
the scheduling for these updates.
'''
import logging
import sched
import time
import datetime
import json
from uk_covid19 import Cov19API
from app import *

logging.basicConfig(filename='sys.log',level=logging.DEBUG)
API_schedule_covid=sched.scheduler(timefunc=time.time, delayfunc=time.sleep)#this needs to be global
config_file=read_config_file()
API_KEY= config_file["API key:"]
LOCATION=config_file["Location:"]
LOCATION_TYPE=config_file["Location type:"]
NATION=config_file["Nation:"]

def  parse_csv_data(csv_filename):
    '''
    Reads the data from a cvs file given and adds each line to a list
        Parameters:
            csv_filename (string): The filename of the csv file to be read
        Returns:
            csv_file_list (list): A list of all the lines in the csv file
        '''
    with open(csv_filename, "r", encoding="UTF-8") as csv_file:
        csv_file_list=[]
        for line in csv_file:
            csv_file_list.append(line)
    return csv_file_list

def process_covid_csv_data(covid_csv_data):
    '''
    Processes the data given to extract some useful data points from a csv file that has been
    read into a list
        Parameters:
            covid_csv_data (list): A list of lines read from a csv file where each line
            contains covid data for a different date
        Returns:
            last7days_cases (int): The total number of cases over the past week
            current_hospital_cases (int): The current number of people in hospital with covid
            total_deaths (int): The total number of people who have ever died from covid in the
            given area
        '''
    stripped_cvs=[]
    for line in covid_csv_data:
        line=line.replace("\n","")
        stripped_cvs.append(line)
    covid_csv_data=stripped_cvs
    future_keys=covid_csv_data[0].split(",")
    cvs_dict={}
    for section in covid_csv_data:
        if section!= covid_csv_data[0]:
            section=section.split(",")
            field_date=section[3]
            temp_dict={}
            for loop in range(0,len(section)):
                if future_keys[loop]!="date":
                    temp_dict[future_keys[loop]]=section[loop]
            cvs_dict[field_date]=temp_dict
    for entry in cvs_dict:
        current_hospital_cases=cvs_dict[entry]["hospitalCases"]
        if current_hospital_cases!="":
            current_hospital_cases=int(current_hospital_cases)
            break
    last7days_cases=0
    count=0
    for entry in cvs_dict:
        daily_new_cases=cvs_dict[entry]["newCasesBySpecimenDate"]
        if daily_new_cases!="":
            count+=1
            if count>1 and count<=8:
                last7days_cases+=int(daily_new_cases)
    for entry in cvs_dict:
        total_deaths=cvs_dict[entry]["cumDailyNsoDeathsByDeathDate"]
        if total_deaths not in ('','None', None):
            total_deaths=int(total_deaths)
            break
    return last7days_cases, current_hospital_cases, total_deaths

def process_covid_API_data(data_dict):
    '''
    Processes the data given to extract some useful data points from a large dictionary
        Parameters:
            data_dict (list): A list of dictionaries where each dictionary contains the covid data
            for a secific date
        Returns:
            last7days_cases (int): The total number of cases over the past week
            current_hospital_cases (int): The current number of people in hospital with covid
            total_deaths (int): The total number of people who have ever died from covid in the
            given area
        '''
    current_hospital_cases=0
    for entry in data_dict:
        current_hospital_cases=entry["hospitalCases"]
        if current_hospital_cases not in ('','None', None):
            current_hospital_cases=int(current_hospital_cases)
            break
    last7days_cases=0
    count=0
    for entry in data_dict:
        daily_new_cases=entry["newCasesBySpecimenDate"]
        if daily_new_cases not in ('','None',None):
            count+=1
            if count>1 and count<=8:
                last7days_cases+=int(daily_new_cases)
    total_deaths=0
    for entry in data_dict:
        total_deaths=entry["cumDailyNsoDeathsByDeathDate"]
        if total_deaths not in ('','None', None):
            total_deaths=int(total_deaths)
            break
    return last7days_cases, current_hospital_cases, total_deaths

def covid_API_request(location="Exeter",location_type="ltla"):
    '''
    makes a request to the covid API to retreive data about the location, hospital cases,
    total deaths, and new cases. Then either saves this data is a file called
    covid_data.json or national_covid_data.json depending on if the location_type
    is a nation or not.
        Parameters:
            location (string): The name of the location that the retrieved data should be from
            location_type (string): The type of the area that the data should be from.
            E.g. nation or ltla
        Returns:
            news_articles: A list of dictionaries where each dictionary gives the covid data
            on a specific date
        '''
    area_type="areaType="+location_type
    area_name="areaName="+location
    data_area = [area_type,area_name]
    data_fields = {
        "date": "date",
        "areaName": "areaName",
        "areaCode": "areaCode",
        "hospitalCases":"hospitalCases",
        "cumDailyNsoDeathsByDeathDate": "cumDailyNsoDeathsByDeathDate",
        "newCasesBySpecimenDate": "newCasesBySpecimenDate",
    }
    api = Cov19API(filters=data_area, structure=data_fields)
    data = api.get_json()
    logging.info('covid update done')
    if location_type=="nation":
        with open('national_covid_data.json', 'w', encoding="UTF-8") as covid_file:
            json.dump(data["data"], covid_file, indent=6)
        return data
    else:
        with open('covid_data.json', 'w', encoding="UTF-8") as covid_file:
            json.dump(data["data"], covid_file, indent=6)
        covid_API_request(NATION,"nation")
    return data



def schedule_covid_updates(update_interval=1,update_name=""):
    '''
    Schedules updates to news API data using an event added to a schedule that is
    in the global namespace
    Parameters:
        update_interval (int): A decimal integer that specifies the time in seconds
        between now and when the update should be scheduled for
        update_name (string): The name of the update
    Returns:
        A dictionary consisting of:
            event: A scheduled event
            update_name (string): The name of the update
        '''
    if not isinstance(update_interval, int):
        seconds=split_time(update_interval)
        now_seconds=split_time( datetime.datetime.now().time().strftime("%H:%M"))
        update_interval=seconds-now_seconds
        if update_interval < 0:
            update_interval=update_interval+(24*60*60)
    event = API_schedule_covid.enter(update_interval, 1, covid_API_request,(LOCATION,LOCATION_TYPE))
    logging.info('covid update scheduled')
    return {"event":event,"title":update_name,"type":"covid"}


def repeat_scheduled_covid_update(update_interval,update_name,scheduled_event):
    '''
    Schedules updates to news API data using an event added to a schedule that is in the
    global namespace
        Parameters:
            update_interval (int): A decimal integer that specifies the time in seconds
            between now and when the update should be scheduled for
            update_name (string): The name of the update
        Returns:
            A dictionary consisting of:
                event: A scheduled event
                update_name (string): The name of the update'''
    if not isinstance(update_interval, int):
        seconds=split_time(update_interval)
        future_time=update_interval
        now_seconds=split_time( datetime.datetime.now().time().strftime("%H:%M"))
        update_interval=seconds-now_seconds
        if update_interval < 0:
            update_interval=update_interval+(24*60*60)
    else:
        future_time=update_interval
    event=API_schedule_covid.enter(update_interval,1, scheduled_event, (future_time,update_name))
    event2=API_schedule_covid.enter(update_interval,1, repeat_scheduled_covid_update, (future_time,update_name,scheduled_event))
    logging.info('repeat covid update scheduled')
    return {"title":update_name,"events":[event,event2],"type":"covid","content":update_interval}
    
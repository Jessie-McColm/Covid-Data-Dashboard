'''
This module runs the flask webpage, running scheduled
events and accepting and proccesing data entered on
the webpage by the user. It sends data (from files or
processed within the code) to the webpage for users to
see.
'''
import os
import logging
from flask import Flask
from flask import render_template
from flask import request
from flask import Markup
from werkzeug.utils import redirect
from app import read_config_file
from covid_data_handler import *
from covid_news_handling import *

app = Flask(__name__)
#array to store deleted items

config_file=read_config_file()
API_KEY= config_file["API key:"]
LOCATION=config_file["Location:"]
NATION=config_file["Nation:"]


logging.basicConfig(filename='sys.log',level=logging.DEBUG)

if os.path.isfile('updates.json'):
    with open('updates.json', 'r', encoding="UTF-8") as updates_file:
        update_data=json.loads(updates_file.read())
else:
    update_data=[]

if os.path.isfile('repeated_updates.json'):
    with open('repeated_updates.json', 'r', encoding="UTF-8") as repeated_updates_file:
        list_of_repeated_updates=json.loads(repeated_updates_file.read())
else:
    list_of_repeated_updates=[]

for update in update_data:
    if update["type"]=="covid":
        addition_to_update=schedule_covid_updates(update["content"],update["title"])
        update["event"]=addition_to_update["event"]
    elif update["type"]=="news":
        addition_to_update= update_news(update["title"],update["content"])
        update["event"]=addition_to_update["event"]

for update in list_of_repeated_updates:
    if update["type"]=="covid":
        addition_to_update=repeat_scheduled_covid_update(update["content"],update["title"],schedule_covid_updates)
        update["events"]=addition_to_update["events"]
    elif update["type"]=="news":
        addition_to_update= repeat_scheduled_news_update(update["content"],update["title"],update_news)
        update["events"]=addition_to_update["events"]

@app.route('/index')
def main_page():
    '''
    Loads and processes all data and sends it to the webpage.
    Also runs the schedule for the data updates and manages user
    inputs and edits data structures accordingly
    Returns:
        render_template(...): A HTML template called index.html
        rendered with all necessary data for display on the website
    '''
    API_schedule_covid.run(blocking=False)
    API_schedule_news.run(blocking=False)

    title=request.args.get("notif")
    if title: #remove widgets
        remove_news_article(title)
        return redirect("/index")

    #reading data from files
    with open('news_data.json', 'r', encoding="UTF-8") as news_file:
        news=json.loads(news_file.read())


    #constructing a list to send news data to web page
    update_name=request.args.get("two")
    news_data=[]
    for item in news:
        news_url=Markup('<a href="'+item["url"] +'">'+" Read full article here" + "</a>")
        content=Markup(item["description"])+news_url
        news_data.append({"title":item["title"],"content":content})
        if len(news_data)>=8:
            break

    if os.path.isfile('national_covid_data.json'):
        with open('national_covid_data.json', 'r', encoding="UTF-8") as covid_file:
            nation_data=json.loads(covid_file.read())
    else:
        logging.info("can't find national_covid_data.json ")

    if os.path.isfile('covid_data.json'):
        with open('covid_data.json', 'r', encoding="UTF-8") as covid_file:
            local_data=json.loads(covid_file.read())
    else:
        logging.info("can't find covid_data.json ")

    #re adds a repeated scheduled event so it can be displayed as a widget
    queue_covid=API_schedule_covid.queue
    queue_news=API_schedule_news.queue

    for item in queue_covid:
        names=item[3]
        if item[2] == schedule_covid_updates:
            try:
                chronology=names[0]
                update_title=names[1]
                event=item
                update_dict={"event":event,"title":update_title,"content":chronology,"type":"covid"}
                if update_dict not in update_data:
                    logging.info('re-added a covid repeated update to the list of updates')
                    update_data.append(update_dict)
            except:
                logging.info('re-adding a covid repeated update to the list of updates failed')

    for item in queue_news:
        names=item[3]
        if item[2] == update_news:
            try:
                chronology=names[1]
                update_title=names[0]
                event=item
                update_dict={"event":event,"title":update_title,"content":chronology,"type":"news"}
                if update_dict not in update_data:
                    logging.info('re-added a news repeated update to the list of updates')
                    update_data.append(update_dict)
            except:
                logging.info('re-adding a covid repeated update to the list of updates failed')



    #removing events

    for entry in update_data:
        if entry["event"] not in API_schedule_news.queue and entry["event"] not in API_schedule_covid.queue:
            update_data.remove(entry)
            logging.info('removed an update that had occured')

    cancel_covid_update,cancel_news_update=False,False

    remove_event=request.args.get("update_item") #removes event from event list +schedule
    if remove_event:
        for entry in update_data:
            if entry["title"]==remove_event:
                try:
                    API_schedule_covid.cancel(entry["event"])
                    cancel_covid_update=entry
                    logging.info("removed "+entry["title"]+(" from update schedule"))
                except:
                    try:
                        API_schedule_news.cancel(entry["event"])
                        cancel_news_update=entry
                        logging.info("removed "+entry["title"]+(" from update schedule"))
                    except:
                        logging.info("removing "+entry["title"]+(" from update schedule failed"))
        if cancel_covid_update:
            update_data.remove(cancel_covid_update)
            logging.info("removed a covid entry from update_data")
        if cancel_news_update:
            update_data.remove(cancel_news_update)
            logging.info("removed a news entry from update_data")
        for entry in list_of_repeated_updates: #REMOVES repeated updates from both queues
            if entry["title"]==remove_event:

                try:
                    API_schedule_covid.cancel(entry["events"][0])
                    API_schedule_covid.cancel(entry["events"][1])
                    logging.info("removed repeated event from the covid schedule")
                except ValueError:
                    logging.info(" failed to remove repeated event from the covid API schedule")


                try:
                    API_schedule_news.cancel(entry["events"][0])
                    API_schedule_news.cancel(entry["events"][1])
                    logging.info("removed repeated event from the news API schedule")
                except ValueError:
                    logging.info("failed to remove repeated event from the news API schedule")
        return redirect("/index")

    if len(update_data)==0 and len(list_of_repeated_updates)!=0:
        logging.info("wiped list_of_repeated_updates and cancelled all events")
        list_of_repeated_updates.clear()
        for item in API_schedule_news.queue:
            API_schedule_news.cancel(item)

        for item in API_schedule_covid.queue:
            API_schedule_covid.cancel(item)

    #schedules events
    if update_name:
        valid_name=True
        #this ensures the same title can't be used
        for item in update_data:
            if update_name == item["title"]:
                valid_name=False
        if valid_name:
            time_input = request.args.get('update')
            if time_input:
                repeat_update=request.args.get("repeat")
                update_covid_data=request.args.get("covid-data")
                update_news_data=request.args.get("news")

                if update_covid_data:
                    event_dict=schedule_covid_updates(time_input,update_name)
                    logging.info("scheduled a covid update")
                    event_dict["content"]=time_input
                    update_data.append(event_dict)
                    if repeat_update:
                        list_of_repeated_updates.append(repeat_scheduled_covid_update(time_input,
                        update_name,schedule_covid_updates))
                        logging.info("scheduled a repeated covid update")

                if update_news_data:
                    event_dict=update_news(update_name,time_input)
                    logging.info("scheduled a news update")
                    event_dict["content"]=time_input
                    update_data.append(event_dict)
                    if repeat_update:
                        list_of_repeated_updates.append(repeat_scheduled_news_update(time_input,
                        update_name,update_news))
                        logging.info("scheduled a repeated news update")
        return redirect("/index")

    update_list_for_web=[]
    #converting into one list - removes excess widgets caused by 2 schedulers
    #also converting to json dumpable lists
    for item in update_data:
        if item == update_data[0]:
            update_list_for_web.append({"title":item["title"],
            "type":item["type"],"content":item["content"]})
        for value in update_list_for_web:
            if value["title"] != item["title"]:
                update_list_for_web.append({"title":item["title"],
            "type":item["type"],"content":item["content"]})

    repeated_updates_to_file=[]
    for item in list_of_repeated_updates:
        repeated_updates_to_file.append({"title":item["title"],
            "type":item["type"],"content":item["content"]})

    with open('updates.json', 'w', encoding="UTF-8") as updates_file:
        json.dump(update_list_for_web, updates_file, indent=6)

    with open('repeated_updates.json', 'w', encoding="UTF-8") as repeated_updates_file:
        json.dump(repeated_updates_to_file, repeated_updates_file, indent=6)


    #processing data
    last7days_cases,current_hospital_cases,total_deaths= process_covid_API_data(local_data)
    last7days_cases_nation, current_hospital_cases_nation, total_deaths_nation=process_covid_API_data(nation_data)
    current_hospital_cases_nation="Current Hospital Cases: "+str(current_hospital_cases_nation)
    total_deaths_nation="Current Total Deaths: "+str(total_deaths_nation)
    logging.info("processed API data")
    #sending data to webpage
    return render_template("index.html", location=LOCATION, local_7day_infections=last7days_cases,
    nation_location=NATION,national_7day_infections=last7days_cases_nation,
    hospital_cases=current_hospital_cases_nation,deaths_total=total_deaths_nation,
    news_articles=news_data, updates=update_list_for_web, image="boon.png")

if __name__=="__main__":
    app.run()

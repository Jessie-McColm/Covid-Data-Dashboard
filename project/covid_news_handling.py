'''
Handles all the updates to news data from the news API and handles
the scheduling for these updates. Also deals with removing deleted
articles'''


import os
import logging
import sched
import time
import datetime
import json
import requests
from app import *
API_schedule_news=sched.scheduler(timefunc=time.monotonic,
delayfunc=time.sleep)
config_file=read_config_file()
API_KEY= config_file["API key:"]
SEARCH_TERMS=config_file["Search terms:"]

logging.basicConfig(filename='sys.log',level=logging.DEBUG)

def news_API_request(covid_terms="Covid COVID-19 coronavirus"):
    '''
    Makes a request to the news_API using the search terms given, then writes the retrieved data
    into a file called news_data.json
        Parameters:
            covid_terms (string): A list of search terms that will be used when requesting data from
            the API
        Returns:
            news_articles: A list of dictionaries where each dictionary gives information about a
            specific article
        '''
    today=datetime.date.today()
    today_date = today.strftime("%Y-%m-%d")
    if covid_terms!=SEARCH_TERMS:
        covid_terms=SEARCH_TERMS
    covid_terms= covid_terms.split()
    count=len(covid_terms)
    for loop in range(0,count):
        term=covid_terms[loop]
        if term!=term.upper():
            covid_terms.append(term.upper())
        if term!=term.lower():
            covid_terms.append(term.lower())
    search_terms="+("
    for term in covid_terms:
        if covid_terms.index(term)==len(covid_terms)-1:
            search_terms=search_terms + term+ ")"
        else:
            search_terms=search_terms+term+" OR "
    url= "https://newsapi.org/v2/everything?"+"q="+search_terms+'&from='+today_date+'&sortBy=relevancy&apiKey='+API_KEY
    response = requests.get(url)
    news_data=response.json()
    news_articles=[]
    if news_data["status"]=="ok":
        news_articles=news_data['articles']
        if os.path.isfile('deleted_articles.json'):
            with open('deleted_articles.json', 'r', encoding="UTF-8") as deleted_articles:
                loaded_data=json.loads(deleted_articles.read())
                for article in news_articles:
                    if article in loaded_data:
                        news_articles.remove(article)
            with open('news_data.json', 'w', encoding="UTF-8") as news_file:
                json.dump(news_articles, news_file, indent=6)
            logging.info("status was ok")
    else:
        logging.info("status was not ok")
        news_articles=["no data"]
    logging.info('news update done')
    return news_articles

def remove_news_article(title:str):
    '''
    Removes a given news article from the json file that stores news articles (news_data.json) and
    writes the deleted article to another json file (deleted_articles.json) so it won't be included
    if the news dats is updated
        Parameters:
            title (string): The title of the news article to be deleted
        '''
    with open('news_data.json', 'r', encoding="UTF-8") as news_file:
        loaded_data=json.loads(news_file.read())
        article=None
        for item in loaded_data:
            if item["title"]==title:
                article=item
        if article in loaded_data:
            loaded_data.remove(article)#may just be able to delete all data
    with open('news_data.json', 'w', encoding="UTF-8") as news_file:
        json.dump(loaded_data, news_file, indent=6)
    if os.path.isfile('deleted_articles.json'):
        with open('deleted_articles.json', 'r', encoding="UTF-8") as removed_articles:
            loaded_data=json.loads(removed_articles.read())
            loaded_data.append(article)
    with open('deleted_articles.json', 'w', encoding="UTF-8") as removed_articles:
        json.dump(loaded_data, removed_articles, indent=6)

def repeat_scheduled_news_update(update_interval:str,update_name:str,scheduled_event):
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
    event=API_schedule_news.enter(update_interval,1, scheduled_event, (update_name,future_time))
    event2=API_schedule_news.enter(update_interval,1, repeat_scheduled_news_update, (future_time,update_name,scheduled_event))
    logging.info('repeated news update scheduled')
    return {"title":update_name,"events":[event,event2],"type":"news","content":update_interval}

def update_news(update_name="",update_interval=1):
    '''
    Schedules updates to news API data using an event added to a schedule that is in the global
    namespace
        Parameters:
            update_interval (int): A decimal integer that specifies the time in seconds between
            now and when the update should be scheduled for update_name (string): The name of
            the update
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
    logging.info('news update done')
    event = API_schedule_news.enter(update_interval, 1, news_API_request, ())
    return {"event":event,"title":update_name,"type":"news"}

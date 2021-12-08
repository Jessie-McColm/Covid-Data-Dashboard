from covid_news_handling import news_API_request
from covid_news_handling import update_news
from covid_news_handling import remove_news_article
from covid_news_handling import repeat_scheduled_news_update

def test_news_API_request():
    assert news_API_request()
    assert news_API_request('Covid COVID-19 coronavirus') == news_API_request()

def test_update_news():
    update_news('test')

def test_remove_news_article():
    remove_news_article("test title 123")

def test_repeat_scheduled_news_update():
    repeat_scheduled_news_update(10,"test title",update_news)

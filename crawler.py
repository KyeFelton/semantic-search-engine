import html
import json
import os
import re
import scrapy
from scrapy.crawler import CrawlerProcess

from spiders import PeopleSpider, 


def clean_text(text):
    remover = re.compile(
        '\\u00a0|\\n|\\t|<[^>]*>|\\ufffd[^\\ufffd]*\\ufffd|&laquo;[^\\&raquo;]*\\&raquo;')
    text = re.sub(remover, '', text)
    text = html.unescape(text)
    apostrophe_replacer = re.compile('&#39;|&rsquo;|\u2019')
    text = re.sub(apostrophe_replacer, "'", text)
    return text


def clean_data(data):
    if type(data) is str:
        data = clean_text(data)
    elif type(data) is dict:
        for k, v in data.items():
            data[k] = clean_data(v)
    elif type(data) is list:
        for i in range(0, len(data)):
            data[i] = clean_data(data[i])
    return data


if __name__ == '__main__':

    # remove old files
    if os.path.exists("./scraped_data/people_raw.json"):
        os.remove("./scraped_data/people_raw.json")
    if os.path.exists("./scraped_data/people.json"):
        os.remove("./scraped_data/people.json")

    # run spiders
    process = CrawlerProcess(settings={
        "FEEDS": {
            "./scraped_data/people_raw.json": {"format": "json"},
        }
    })
    process.crawl(PeopleSpider)
    process.start()

    # clean data
    with open('./scraped_data/people_raw.json') as f:
        data = json.loads(f.read())

    combined = {}
    for item in data:
        clean_data(item)
        if item['id'] in combined:
            combined[item['id']].update(item)
        else:
            combined[item['id']] = item

    # save files
    with open('./scraped_data/people.json', 'w') as f:
            f.write(json.dumps(list(combined.values())))
import html
import json
import os
import re
import scrapy
import sys
import shutil
from scrapy.crawler import CrawlerProcess

from spiders import PageSpider, PeopleSpider


def replace_pattern(old_pattern, new_pattern, text):
    modifier = re.compile(old_pattern)
    return re.sub(modifier, new_pattern, text)


def clean_text(data):

    # remove html tags and syntax from text
    if type(data) is str:
        data = replace_pattern('<\/p>|<\/h.>', '. ', data)
        data = replace_pattern('</li>', ', ', data)
        data = replace_pattern('\\u00a0|\\n|\\t|<[^>]*>|\\ufffd[^\\ufffd]*\\ufffd|&laquo;[^\\&raquo;]*\\&raquo;', ' ', data)
        data = html.unescape(data)
        data = replace_pattern('\ {2,}', ' ', data)
        data = replace_pattern('[\ |,]{3,}', ', ', data)
        data = replace_pattern('[\ |.|,]{3,}', '. ', data)
        data = replace_pattern('[( .,)]*:[( .,)]*', ': ', data)
        data = data.strip()

    # traverse through dict to clean all text values
    elif type(data) is dict:
        for k, v in data.items():
            data[k] = clean_text(v)
    elif type(data) is list:
        for i in range(0, len(data)):
            data[i] = clean_text(data[i])
            
    return data


def merge_ids(data):
    merged = {}
    for item in data:
        if item['id'] in merged:
            merged[item['id']].update(item)
        else:
            merged[item['id']] = item
    return merged

def clean_data(name, merge):

    filename = '../scraped_data/' + name + '_raw.json'

    # load the scraped data
    with open(filename) as f:
        data = json.loads(f.read())

    # clean the data
    if merge:
        data = merge_ids(data)
    data = clean_text(data)

    # save the cleaned data
    filename = '../scraped_data/' + name + '.json'
    with open(filename, 'w') as f:
        try:
            f.write(json.dumps(list(data.values())))
        except AttributeError as e:
            f.write(json.dumps(list(data)))


if __name__ == '__main__':

    # remove old data
    try:
        shutil.rmtree('../scraped_data')
    except OSError as e:
        pass
    
    # run spiders
    process = CrawlerProcess()
    process.crawl(PageSpider)
    process.crawl(PeopleSpider)
    process.start()

    # clean the data
    clean_data('page', False)
    clean_data('people', True)
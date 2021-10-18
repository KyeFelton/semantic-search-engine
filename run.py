import argparse
import importlib
import io
import json
import os
import pandas as pd
import scrapy.crawler as sc
import shutil
import stardog
import subprocess
import sys

from config import *


ap = argparse.ArgumentParser()

def get_class(package, module):
    module_name = f'{package}.{module}'
    class_name = f'{package.title()}{module.title()}'
    clas = getattr(importlib.import_module(module_name), class_name)
    return clas

if __name__ == '__main__':
    
    ap.add_argument('-s', '--scrape', required=False, help='Scrape new data from the web', action='store_true')
    ap.add_argument('domains', help='Specify which domains to build the KG', nargs='+')
    domains =  vars(ap.parse_args())['domains']
         
    
    # Create the data directory
    for d in domains:
        data_dir = f'{root_dir}/{d}/data/'
        if not os.path.exists(data_dir):
            os.mkdir(data_dir)
    
    # Crawl and scrape the domain
    if vars(ap.parse_args())['scrape']:
        process = sc.CrawlerProcess(settings=crawler_settings)
        for d in domains:
            spider_class = get_class(d, 'spider')
            process.crawl(spider_class)
        print('Scraping usyd web domain...')
        process.start()
        for d in domains:
            ifile = f'{root_dir}/{d}.json'
            ofile = f'{root_dir}/{d}/data/scraped.json'
            os.replace(ifile, ofile)
        print('Finished scraping')

    # Clean the data
    for d in domains:
        if not os.path.exists(f'{root_dir}/{d}/data/scraped.json'):
            print(f'Unable to locate scraped data for {d}. Please include "-s" option to perform a scrape.')
            exit(4)
        print(f'Cleaning: {d}')
        cleaner_class = get_class(d, 'cleaner')
        cleaner = cleaner_class(root_dir)
        cleaner.clean()
    print(f'Finished cleaning data')

    # Build kg and docs
    for d in domains:
        print(f'Building: {d}')
        builder_class = get_class(d, 'builder')
        builder = builder_class(root_dir)
        builder.build()
    print(f'Finished building kg')

    # Create db
    with stardog.Admin(**conn_details) as admin:
        db_name_list = [db.name for db in admin.databases()]
        if db_name in db_name_list:
            db = admin.database(db_name)
            db.drop()
        db = admin.new_database(db_name, {'search.enabled': True, 'docs.opennlp.models.path': f'{root_dir}/nlp/OpenNLP'})
        print(f'Created database: {db_name}')

    # Upload kg to db
    with stardog.Connection(db_name, **conn_details) as conn:
        for d in domains:
            print(f'Uploading {d} kg to {db_name}')
            conn.begin()
            conn.add(stardog.content.File(f'./{d}/data/kg.json'))
            conn.commit()
        print(f'Finished uploading data')
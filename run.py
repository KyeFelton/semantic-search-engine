import argparse
import json
import os
import pandas as pd
import shutil
import stardog
import subprocess
import sys

from packages import *

from scrapy.crawler import CrawlerProcess

from config import *
import io

ap = argparse.ArgumentParser()

if __name__ == '__main__':
    
    ap.add_argument('-s', '--spiders', required=False, help='Run the spiders', action='store_true')
    ap.add_argument('-c', '--cleaners', required=False, help='Run the cleaners', action='store_true')
    ap.add_argument('-b', '--builders', required=False, help='Run the builders', action='store_true')
    ap.add_argument('-t', '--testers', required=False, help='Run the testers', action='store_true')
    ap.add_argument('-a', '--all', required=False, help='Run the spiders, cleaners, builders and testers', action='store_true')
    ap.add_argument('-d', '--domains', required=True, help='Specify which domains should be constructued', nargs='*')
    
    domains =  vars(ap.parse_args())['domains']
    
    for d in domains:
        if d not in valid_domains:
            print(f'Invalid entity type: {d}.\n The following entity types are accepted: {valid_domains}')
            exit(1)
    
    if vars(ap.parse_args())['spiders'] or vars(ap.parse_args())['all']:
        # Crawl and scrape the domain
        process = CrawlerProcess(settings=crawler_settings)
        for d in domains:
            spider_name = d.title() + 'Spider'
            spider = getattr(sys.modules[__name__], spider_name)
            process.crawl(spider)
        print('Scraping usyd web domain...')
        process.start()
        for d in domains:
            ifile = './' + d + '.json'
            ofile = scraped_path + d + '.json'
            os.replace(ifile, ofile)
        print('Finished scraping')
    
    if vars(ap.parse_args())['cleaners'] or vars(ap.parse_args())['all']:
        # Clean the data
        for d in domains:
            if d in nlp_domains:
                print(f'Cleaning data for: {d}')          
                ifile = scraped_path + d + '.json'
                ofile = cleaned_path + d + '.json'
                clean(ifile, ofile, d=='person')
        print(f'Finished cleaning data')

    if vars(ap.parse_args())['builders'] or vars(ap.parse_args())['all']:
        # Build kg
        for d in domains:
            kg = {}
            kg['@context'] = {}
            kg['@graph'] = []
            print(f'Building: {d}')
            if d in nlp_domains:
                ifile = cleaned_path + d + '.json'
            else:
                ifile = scraped_path + d + '.json'
            builder_name = d.title() + 'Builder'
            builder_class = getattr(sys.modules[__name__], builder_name)
            builder = builder_class(ifile)
            kg['@context'].update(builder.context)
            kg['@graph'].extend(builder.kg)

            if os.path.exists(kg_path + d + '.json'):
                os.remove(kg_path + d + '.json')
            with open(kg_path + d + '.json', 'w') as f:
                f.write(json.dumps(kg))
        print(f'Finished building kg')
        
        # Upload to db
        with stardog.Admin(**conn_details) as admin:
            db_name_list = [db.name for db in admin.databases()]
            if db_name in db_name_list:
                db = admin.database(db_name)
                db.drop()
            db = admin.new_database(db_name)

            with stardog.Connection(db_name, **conn_details) as conn:
                print(f'Uploading to stardog')
                for d in domains:
                    conn.begin()
                    conn.add(stardog.content.File(kg_path + d + '.json'))
                    conn.commit()
                print(f'Finished upload')

        
    if vars(ap.parse_args())['testers'] or vars(ap.parse_args())['all']:
        with stardog.Admin(**conn_details) as admin:
            # Run tests
            conn = stardog.Connection(db_name)
            run_sparql_tests(conn, db_name, sparql_tests_path)
  
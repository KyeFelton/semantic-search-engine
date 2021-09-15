import json
import scrapy

class EventSpider(scrapy.Spider):
    name = 'event'
    allowed_domains = ['www.sydney.edu.au']
    start_urls = ['https://whatson.sydney.edu.au/graphql/event']

    custom_settings = {
        'FEEDS': {
            'event.json': {'format': 'json'},
        }
    }

    def parse(self, response):
        data = {}
        if response.body:
            data['events'] = json.loads(response.body)
            yield data
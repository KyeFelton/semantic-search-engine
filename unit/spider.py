import json
import scrapy
from scrapy.spiders import SitemapSpider


class UnitSpider(SitemapSpider):
    name = 'unit'
    allowed_domains = ['www.sydney.edu.au']
    sitemap_urls = ['http://www.sydney.edu.au/robots.txt']
    sitemap_rules = [
        ('/courses/units-of-study/', 'parse'), 
    ]
    custom_settings = {
        'FEEDS': {
            'unit.json': {'format': 'json'},
        }
    }

    def parse(self, response):
        url = response.request.url.replace('.html', '.coredata.json')
        yield scrapy.Request(url, callback=self.parse_data)
        
    def parse_data(self, response):
        print(response.request.url)
        if response.body:
            yield {response.request.url: json.loads(response.body)}
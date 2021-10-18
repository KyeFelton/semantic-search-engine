import json
import scrapy
from scrapy.spiders import SitemapSpider


class SubjectSpider(SitemapSpider):
    name = 'subject'
    allowed_domains = ['www.sydney.edu.au']
    sitemap_urls = ['http://www.sydney.edu.au/robots.txt']
    sitemap_rules = [
        ('/courses/subject-areas/', 'parse'),
    ]
    custom_settings = {
        'FEEDS': {
            'subject.json': {'format': 'json'},
        }
    }

    def parse(self, response):
        url = response.request.url.replace('.html', '.coredata.json')
        yield scrapy.Request(url, callback=self.parse_data)
        url = response.request.url.replace('.html', '.explorer.json')
        yield scrapy.Request(url, callback=self.parse_data)
        
    def parse_data(self, response):
        print(response.request.url)
        if response.body:
            yield {response.request.url: json.loads(response.body)}
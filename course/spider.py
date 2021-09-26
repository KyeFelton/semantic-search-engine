import json
import scrapy
from scrapy.spiders import SitemapSpider

class CourseSpider(SitemapSpider):
    name = 'course'
    allowed_domains = ['www.sydney.edu.au']
    sitemap_urls = ['http://www.sydney.edu.au/robots.txt']
    sitemap_rules = [
        ('/courses/courses/', 'parse'), 
    ]
    custom_settings = {
        'FEEDS': {
            'course.json': {'format': 'json'},
        }
    }

    def parse(self, response):
        url = response.request.url.replace('.html', '.coredata.json')
        yield scrapy.Request(url, callback=self.parse_data)
        
    def parse_data(self, response):
        data = {}
        if response.body:
            data['course'] = json.loads(response.body)
            yield data
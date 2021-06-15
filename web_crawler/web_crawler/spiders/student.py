import scrapy


class StudentSpider(scrapy.Spider):
    name = 'student'
    allowed_domains = ['www.sydney.edu.au']
    start_urls = ['http://www.sydney.edu.au/']

    def parse(self, response):
        pass

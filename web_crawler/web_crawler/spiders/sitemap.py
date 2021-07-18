import scrapy
from web_crawler.items import URLItem
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import SitemapSpider, Rule


class SitemapSpider(SitemapSpider):
    name = 'sitemap'
    allowed_domains = ['www.sydney.edu.au']
    sitemap_urls = ['http://www.sydney.edu.au/robots.txt']
    sitemap_rules = [
        ('/engineering/', 'parse'),
    ]

    def parse(self, response):
        yield URLItem(url=response.request.url)

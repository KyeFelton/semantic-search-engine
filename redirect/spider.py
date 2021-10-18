import json
import scrapy
import validators

from engineering.categoriser import is_publication


class RedirectSpider(scrapy.Spider):
    # handle_httpstatus_list = [404, 500]
    name = 'redirect'
    # download_delay = 0.1

    custom_settings = {
        'FEEDS': {
            'redirect.json': {'format': 'json'},
        }
    }

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.failed_urls = []

    # @classmethod
    # def from_crawler(cls, crawler, *args, **kwargs):
    #     spider = super(RedirectSpider, cls).from_crawler(crawler, *args, **kwargs)
    #     crawler.signals.connect(spider.handle_spider_closed, scrapy.signals.spider_closed)
    #     return spider

    def start_requests(self):

        def traverse(data, links):
            if type(data) is dict:
                for k, v in data.items():
                    links.update(traverse(v, links))
            elif type(data) is list:
                for i in data:
                    links.update(traverse(i, links))
            elif type(data) is str:
                data = data.replace(' ', '')
                if validators.url(data) and not is_publication(data, None, None):
                    links.add(data)
            return links

        with open('./engineering/data/cleaned.json') as f:
            source = json.loads(f.read())
        urls = traverse(source, set())
        with open('./person/data/cleaned.json') as f:
            source = json.loads(f.read())
        urls.update(traverse(source, set()))
        urls = list(urls)
        with open('./redirect/data/urls.json', 'w') as f:
            f.truncate(0)
            f.write(json.dumps(urls))
        window = len(urls)
        offset = 0
        for i in range(offset, min(len(urls), offset + window)):
            url = urls[i]
            print(f'{i}: {url}')
            yield scrapy.Request(url, callback=self.parse_data, meta={'source': url})

    def parse_data(self, response):
        # if response.status in self.handle_httpstatus_list:
        # self.crawler.stats.inc_value('failed_url_count')
        # self.failed_urls.append(response.url)
        # yield {response.meta['source']: response.status}
        # else:
        yield {response.meta['source']: response.request.url}

    # def handle_spider_closed(self, reason):
    #     self.crawler.stats.set_value('failed_urls', ', '.join(self.failed_urls))
    #
    # def process_exception(self, response, exception, spider):
    #     ex_class = "%s.%s" % (exception.__class__.__module__, exception.__class__.__name__)
    #     self.crawler.stats.inc_value('downloader/exception_count', spider=spider)
    #     self.crawler.stats.inc_value('downloader/exception_type_count/%s' % ex_class, spider=spider)
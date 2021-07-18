import json
import scrapy

# Obtain contact info from: https://www.sydney.edu.au/perl-bin/phlookup.cgi
# Check three pages of each form to ensure all data is captured
# Stretch: a) differentiate between headings, text and lists b) add images


class EngineeringSpider(scrapy.Spider):
    name = 'engineering'
    allowed_domains = ['www.sydney.edu.au']
    start_urls = ['https://www.sydney.edu.au/engineering/about.html']
    
    def parse(self, response):
        with open('sitemap.json') as json_file:
            data = json.load(json_file)
            for item in data:
                yield scrapy.Request(item['url'], callback=self.parse_page)


    def parse_page(self, response):
        page = {
            'url': response.url,
            'category': self.extract(response, '//div[@class="contentType"]', True),
            'title': self.extract(response, '//h1[@class="pageTitle "]/div', True),
            'subtitle': self.extract(response, '//div[@class="pageStrapline"]/div', True),
            'date': self.extract(response, '//div[@class="publishDate"]/span', True),
            'summary': self.extract(response, '//div[@class="b-summary b-component b-text--size-larger cq-editable-inline-text "]', True),
            'call_to_action': {
                'text': self.extract(response, '//div[@class="call-to-action parbase"]/a/@data-value', False),
                'href': self.extract(response, '//div[@class="call-to-action parbase"]/a/@href', False),
            },
            'content': self.get_content(response),
            'accordions': self.get_accordions(response),
            'articles': self.get_articles(response),
            'news': self.get_news(response),
            'call_outs': self.get_call_outs(response),
            'podcasts': self.get_podcasts(response),
        }
        yield page

    def get_content(self, response):
        content = []
        for section in response.xpath('//div[contains(@class, "content-container")]/div'):
            section_content = ''
            for paragraph in section.xpath('*'):
                section_content += paragraph.extract()
            content.append(section_content)
        return content

    def get_accordions(self, response):
        accordions = []
        for group in response.xpath('//div[@class="accordion parbase"]/div/div'):
            for item in group.xpath('div'):
                accordion = {}
                accordion['heading'] = item.xpath('div/h4/a/@title').extract()
                body = ''
                for paragraph in item.xpath('div/div/div/*'):
                    body += paragraph.extract().strip()
                accordion['body'] = body
                accordions.append(accordion)
        return accordions

    def get_articles(self, response):
        articles = []
        for article_selector in response.xpath('//div[@class="featured-article parbase"]'):
            article = {}
            article['href'] = self.extract(article_selector, 'a/@href', False)
            article['category'] = self.extract(article_selector, 'a/div[@class="b-image-link"]/div[1]', True)
            article['title'] = self.extract(article_selector, 'a/div[@class="b-image-link"]/div[2]/div[1]/h3', True)
            article['summary'] = self.extract(article_selector, 'a/div[@class="b-image-link"]/div[2]/div[2]/div[2]', True)
            articles.append(article)
        return articles

    def get_news(self, response):
        news = []
        for news_selector in response.xpath('//div[contains(@class, "news-article-page")]'):
            news.append(self.extract(news_selector, 'a/@href'), False)
        return news
    
    def get_call_outs(self, response):
        call_outs = []
        for call_out_selector in response.xpath('//div[@class="call-out parbase"]/div'):
            call_out = {}
            call_out['title'] = call_out_selector.xpath('div[1]/h3/text()').extract_first().strip()
            call_out['quote'] = call_out_selector.xpath('div[3]/div/text()').extract_first().strip()
            call_out['text'] = call_out_selector.xpath('div[3]/a/text()').extract_first().strip()
            call_out['href'] = call_out_selector.xpath('div[3]/a/@href').extract_first()
            call_outs.append(call_out)
        return call_outs

    def get_podcasts(self, response):
        podcasts = []
        for podcast_selector in response.xpath('//div[@class="podcast "]'):
            podcast = {}
            podcast['title'] = podcast_selector.xpath('h4/div/text()').extract_first().strip()
            podcast['summary'] = podcast_selector.xpath('div[@class="podcastSummary"]/p/text()').extract_first().strip()
            podcast['href'] = podcast_selector.xpath('div[@class="downloadLink"]/a/@href').extract_first()
            podcasts.append(podcast)
        return podcasts

    def extract(self, response, path, isText):
        if isText:
            data = response.xpath(path + '/text()').extract_first()
            if data is not None and data.strip() is '':
                data = response.xpath(path + '/p/text()').extract_first()
            if data is not None:
                data = data.strip()
        else:
            data = response.xpath(path).extract()
        return data

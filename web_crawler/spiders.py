import json
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import SitemapSpider, Rule

# Obtain contact info from: https://www.sydney.edu.au/perl-bin/phlookup.cgi
# Check three pages of each form to ensure all data is captured
# Add commenting and documentation for the code
# Add self.extract to each function to keep consistent
# Stretch: a) differentiate between headings, text and lists b) add images


class PageSpider(SitemapSpider):
    name = 'sitemap'
    allowed_domains = ['www.sydney.edu.au']
    sitemap_urls = ['http://www.sydney.edu.au/robots.txt']
    sitemap_rules = [
        ('/engineering/', 'parse'),
    ]
    custom_settings = {
        "FEEDS": {
            '../scraped_data/page_raw.json': {"format": "json"},
        }
    }

    def parse(self, response):
        page = {
            'url': response.request.url,
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
            article['category'] = self.extract(
                article_selector, 'a/div[@class="b-image-link"]/div[1]', True)
            article['title'] = self.extract(
                article_selector, 'a/div[@class="b-image-link"]/div[2]/div[1]/h3', True)
            article['summary'] = self.extract(
                article_selector, 'a/div[@class="b-image-link"]/div[2]/div[2]/div[2]', True)
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
            call_out['title'] = call_out_selector.xpath(
                'div[1]/h3/text()').extract_first().strip()
            call_out['quote'] = call_out_selector.xpath(
                'div[3]/div/text()').extract_first().strip()
            call_out['text'] = call_out_selector.xpath(
                'div[3]/a/text()').extract_first().strip()
            call_out['href'] = call_out_selector.xpath(
                'div[3]/a/@href').extract_first()
            call_outs.append(call_out)
        return call_outs

    def get_podcasts(self, response):
        podcasts = []
        for podcast_selector in response.xpath('//div[@class="podcast "]'):
            podcast = {}
            podcast['title'] = podcast_selector.xpath(
                'h4/div/text()').extract_first().strip()
            podcast['summary'] = podcast_selector.xpath(
                'div[@class="podcastSummary"]/p/text()').extract_first().strip()
            podcast['href'] = podcast_selector.xpath(
                'div[@class="downloadLink"]/a/@href').extract_first()
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


class PeopleSpider(scrapy.Spider):
    name = 'people'
    allowed_domains = ['www.sydney.edu.au']
    start_urls = [
        'https://www.sydney.edu.au/engineering/about/our-people/academic-staff.html']
    headers = {
        'accept': 'application/json',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }
    custom_settings = {
        "FEEDS": {
            '../scraped_data/people_raw.json': {"format": "json"},
        }
    }

    def parse(self, response):
        headers = self.headers
        types = [('academic-staff', '1'), ('research-student', '2')]
        for typ in types:
            headers['referer'] = 'https://www.sydney.edu.au/engineering/about/our-people/' + typ[0] + '.html'
            url = 'https://www.sydney.edu.au/AcademicProfiles/interfaces/rest/getMembersByCodeAndJobType/5000053030H0000/' + \
                typ[1]
            request = scrapy.Request(
                url, callback=self.parse_person, headers=headers, meta={'type': typ[0]})
            yield request

    def parse_person(self, response):
        categories = [
            'getHrPerson',
            'getGrantDetails',
            'getAuthorDetails',
            'getPublishingActiveAuthor',
            'getAuthorsNewKeywords',
            'getHonoursSupervisor',
            'getExpertiseDetails',
            'getSupervisedStudents',
            'getResearchSupervisor',
            'getCentreListForStaff',
            'getBookSellingLinks',
            'getCollaborator',
            'getThesisList'
        ]

        for person in json.loads(response.body):
            headers = self.headers
            headers['referer'] = 'http://www.sydney.edu.au/engineering/about/our-people/' + \
                response.meta['type'] + '/' + \
                person['urlid'].replace('.', '-') + '.html'
            for category in categories:
                url = 'https://www.sydney.edu.au/AcademicProfiles/interfaces/rest/' + \
                    category + '/' + person['urlid']
                yield scrapy.Request(url, callback=self.parse_data, headers=headers, meta={'id': person['urlid'], 'type': response.meta['type'], 'category': category})

    def parse_data(self, response):
        data = {}
        data['id'] = response.meta['id']
        data['type'] = response.meta['type']
        if response.body:
            data[response.meta['category']] = json.loads(response.body)
        else:
            data[response.meta['category']] = None
        yield data
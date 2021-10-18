from scrapy.spiders import SitemapSpider


class EngineeringSpider(SitemapSpider):
    name = 'engineering'
    allowed_domains = ['www.sydney.edu.au']
    sitemap_urls = ['http://www.sydney.edu.au/robots.txt']
    sitemap_rules = [
        ('/engineering/', 'parse'),
    ]
    custom_settings = {
        'FEEDS': {
            'engineering.json': {'format': 'json'},
        }
    }

    def parse(self, response):
        page = {
            'url': response.request.url.replace(' ', ''),
            'category': self.extract_text(response, '//div[@class="contentType"]'),
            'title': self.extract_text(response, '//h1[@class="pageTitle "]/div'),
            'subtitle': self.extract_text(response, '//div[@class="pageStrapline"]/div'),
            'date': self.extract_text(response, '//div[@class="publishDate"]/span'),
            'summary': self.extract_text(response, '//div[@class="b-summary b-component b-text--size-larger cq-editable-inline-text "]'),
            'content': self.get_content(response),
            'accordions': self.get_accordions(response),
            'articles': self.get_articles(response),
            'news': self.get_news(response),
            'call_outs': self.get_call_outs(response),
            'contacts': self.get_contacts(response),
            'location': self.get_location(response)
        }
        yield page

    def get_content(self, response):
        content = []
        section_content = {'heading': '$FIRST$', 'body': '', 'links': []}
        for section in response.xpath('//div[contains(@class, "content-container")]/div | //div[contains(@class, "heading")]'):
            if 'heading' in section.attrib['class']:
                content.append(section_content)
                section_content = {'heading': section.xpath('*/text()').extract_first(), 'body': '', 'links': []}
            else:
                for paragraph in section.xpath('*'):
                    if paragraph.root.tag in {'h1', 'h2', 'h3', 'h4', 'h5', 'h6'}:
                        content.append(section_content)
                        section_content = {'heading': paragraph.extract(), 'body': '', 'links': []}
                    elif paragraph.root.tag in {'p', 'ul'}:
                        section_content['body'] += paragraph.extract()
            for link in section.xpath('*//a | a'):
                if 'href' in link.attrib and link.attrib['href'][0] != '#':
                    section_content['links'].append({
                        'href': link.attrib['href'],
                        'text': link.extract()
                    })
        content.append(section_content)
        return content

    def get_accordions(self, response):
        accordions = []
        for group in response.xpath('//div[@class="accordion parbase"]/div/div'):
            for item in group.xpath('div'):
                accordion = {}
                accordion['heading'] = item.xpath('div/h4/a/@title').extract_first()
                accordion['body'] = ''
                for paragraph in item.xpath('div/div/div/*'):
                    accordion['body'] += paragraph.extract().strip()
                accordion['links'] = []
                for link in item.xpath('*//a | a'):
                    if 'href' in link.attrib and link.attrib['href'][0] != '#':
                        accordion['links'].append({
                            'href': link.attrib['href'],
                            'text': link.extract()
                        })
                accordions.append(accordion)
        return accordions

    def get_articles(self, response):
        articles = []
        for selector in response.xpath('//div[@class="featured-article parbase"]'):
            article = {}
            article['href'] = selector.xpath('a/@href').extract_first()
            article['category'] = self.extract_text(selector, 'a/div[@class="b-image-link"]/div[1]')
            article['title'] = self.extract_text(selector, 'a/div[@class="b-image-link"]/div[2]/div[1]/h3')
            article['summary'] = self.extract_text(selector, 'a/div[@class="b-image-link"]/div[2]/div[2]/div[2]')
            articles.append(article)
        return articles

    def get_news(self, response):
        news = []
        for selector in response.xpath('//div[contains(@class, "news-article-page")]'):
            news.append(selector.xpath('a/@href').extract_first())
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

    def get_contacts(self, response):
        return response.xpath('//div[contains(@class, "b-contact-information ")]').extract_first()

    def get_location(self, response):
        return response.xpath('//div[@class="locationAddress"]').extract_first()

    def extract_text(self, response, path):
        data = response.xpath(path + '/text()').extract_first()
        if data and data.strip() == '':
            data = response.xpath(path + '/p/text()').extract_first()
        return data
import json
import scrapy
from scrapy.crawler import CrawlerProcess

class PeopleSpider(scrapy.Spider):
    name = 'people'
    allowed_domains = ['www.sydney.edu.au']
    start_urls = ['https://www.sydney.edu.au/engineering/about/our-people/academic-staff.html']
    headers = {
        'accept': 'application/json',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }

    def parse(self, response):
        headers = self.headers
        types = [('academic-staff', '1'), ('research-student', '2')]
        for typ in types:
            headers['referer'] = 'https://www.sydney.edu.au/engineering/about/our-people/' + typ[0] + '.html'
            url = 'https://www.sydney.edu.au/AcademicProfiles/interfaces/rest/getMembersByCodeAndJobType/5000053030H0000/' + typ[1]
            request = scrapy.Request(url, callback=self.parse_person, headers=headers, meta={'type': typ[0]})
            yield request

    def parse_person(self, response):
        categories = ['getHrPerson', 'getGrantDetails', 'getAuthorDetails']
        if (response.meta['type'] == 'research-student'):
            categories.append('getThesisList')
        elif (response.meta['type'] == 'academic-staff'):
            categories.append('getCollaborator')
        
        for person in json.loads(response.body):
            headers = self.headers
            headers['referer'] = 'http://www.sydney.edu.au/engineering/about/our-people/' + response.meta['type'] + '/' + person['urlid'].replace('.', '-') + '.html'
            for category in categories:
                url = 'https://www.sydney.edu.au/AcademicProfiles/interfaces/rest/' + category + '/' + person['urlid']
                yield scrapy.Request(url, callback=self.parse_data, headers=headers, meta ={'id': person['urlid']})

    def parse_data(self, response):       
        data = json.loads(response.body)
        data['id'] = response.meta['id']
        yield data
            



            
            # url = 'https://www.sydney.edu.au/AcademicProfiles/interfaces/rest/getGrantDetails/' + person['urlid']
            # yield scrapy.Request(url, callback=self.parse_data, headers=headers)
            # url = 'https://www.sydney.edu.au/AcademicProfiles/interfaces/rest/getExpertiseDetails/' + person['urlid']
            # yield scrapy.Request(url, callback=self.parse_data, headers=headers)
            # url = 'https://www.sydney.edu.au/AcademicProfiles/interfaces/rest/getAuthorDetails/' + person['urlid']
            # yield scrapy.Request(url, callback=self.parse_data, headers=headers)
            # url = 'https://www.sydney.edu.au/AcademicProfiles/interfaces/rest/getCollaborator/' + person['urlid']
            # yield scrapy.Request(url, callback=self.parse_data, headers=headers)


# run spider
process = CrawlerProcess()
process.crawl(PeopleSpider)
process.start()

# types = [('academic-staff', '1'), ('research-student', '2')]
# for typ in types:
#     header = 'https://www.sydney.edu.au/engineering/about/our-people/' + typ[0] + '.html'
#     url = 'https://www.sydney.edu.au/AcademicProfiles/interfaces/rest/getMembersByCodeAndJobType/5000053030H0000/' + typ[1]
#     print(header)
#     print(url)
import json
import scrapy
from spiders.headers import default_header

categories = [ 'getHrPerson', 'getGrantDetails', 'getAuthorDetails', 'getPublishingActiveAuthor', 'getAuthorsNewKeywords', 'getHonoursSupervisor', 'getExpertiseDetails', 'getSupervisedStudents', 'getResearchSupervisor', 'getCentreListForStaff', 'getBookSellingLinks', 'getCollaborator', 'getThesisList' ]

class PersonSpider(scrapy.Spider):
    name = 'person'
    allowed_domains = ['www.sydney.edu.au']
    start_urls = [
        'https://www.sydney.edu.au/engineering/about/our-people/academic-staff.html']

    custom_settings = {
        'FEEDS': {
            'person.json': {'format': 'json'},
        }
    }

    def parse(self, response):
        header = default_header
        types = [('academic-staff', '1'), ('research-student', '2')]
        for typ in types:
            header['referer'] = 'https://www.sydney.edu.au/engineering/about/our-people/' + typ[0] + '.html'
            url = 'https://www.sydney.edu.au/AcademicProfiles/interfaces/rest/getMembersByCodeAndJobType/5000053030H0000/' + \
                typ[1]
            request = scrapy.Request(
                url, callback=self.parse_person, headers=header, meta={'type': typ[0]})
            yield request

    def parse_person(self, response):
        for person in json.loads(response.body):
            header = default_header
            header['referer'] = 'http://www.sydney.edu.au/engineering/about/our-people/' + \
                response.meta['type'] + '/' + \
                person['urlid'].replace('.', '-') + '.html'
            for category in categories:
                url = 'https://www.sydney.edu.au/AcademicProfiles/interfaces/rest/' + \
                    category + '/' + person['urlid']
                yield scrapy.Request(url, callback=self.parse_data, headers=header, meta={'id': person['urlid'], 'type': response.meta['type'], 'category': category})

    def parse_data(self, response):
        data = {}
        data['id'] = response.meta['id']
        data['type'] = response.meta['type']
        if response.body:
            data[response.meta['category']] = json.loads(response.body)
        else:
            data[response.meta['category']] = None
        yield data
import json
import scrapy

from web_crawler.items import JSONItem

class StaffIDSpider(scrapy.Spider):
    name = 'staff_id'
    allowed_domains = ['www.sydney.edu.au']
    start_urls = ['https://www.sydney.edu.au/engineering/about/our-people/academic-staff.html']
    headers = {
        'accept': 'application/json',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'referer': 'https://www.sydney.edu.au/engineering/about/our-people/academic-staff.html',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }

    def parse(self, response):
        url = 'https://www.sydney.edu.au/AcademicProfiles/interfaces/rest/getMembersByCodeAndJobType/5000053030H0000/1'
        request = scrapy.Request(url, callback=self.parse_staff_id, headers=self.headers)
        yield request

    def parse_staff_id(self, response):
        raw_data = response.body
        data = json.loads(raw_data)
        yield JSONItem(json=data)


# import json
# import scrapy

# from web_crawler.items import PersonItem

# class StaffSpider(scrapy.Spider):
#     name = 'academic_staff'
#     allowed_domains = ['www.sydney.edu.au']
#     start_urls = ['https://www.sydney.edu.au/engineering/about/our-people/academic-staff.html']
#     headers = {
#         'accept': 'application/json',
#         'accept-encoding': 'gzip, deflate, br',
#         'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
#         'referer': 'https://www.sydney.edu.au/engineering/about/our-people/academic-staff.html',
#         'sec-fetch-mode': 'cors',
#         'sec-fetch-site': 'same-origin',
#         'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36',
#         'x-requested-with': 'XMLHttpRequest',
#     }

#     def parse(self, response):
#         url = 'https://www.sydney.edu.au/AcademicProfiles/interfaces/rest/getMembersByCodeAndJobType/5000053030H0000/1'
#         request = scrapy.Request(url, callback=self.parse_people, headers=self.headers)
#         yield request

#     def parse_people(self, response):
#         raw_data = response.body
#         data = json.loads(raw_data)
#         for person in data:
#             url = 'https://www.sydney.edu.au/AcademicProfiles/interfaces/rest/getHrPerson/' + person['urlid']
#             headers = self.headers
#             headers['referer'] = 'http://www.sydney.edu.au/engineering/about/our-people/academic-staff/' + person['urlid'].replace('.', '-') + '.html'
#             yield scrapy.Request(url, callback=self.parse_person, headers=headers)

#     def parse_person(self, response):
#         raw_data = response.body
#         data = json.loads(raw_data)
#         yield PersonItem(given_names=data['givenName'], surname=data['surname'], email=data['emailAddress'])

import json
import scrapy


class StudentSpider(scrapy.Spider):
    name = 'student'
    allowed_domains = ['www.sydney.edu.au']
    start_urls = ['https://www.sydney.edu.au/engineering/about/our-people/research-students.html']
    
    def parse(self, response):
        with open('student_id.json') as json_file:
            data = json.load(json_file)[0]['json']
            for person in data:
                headers = {
                    'accept': 'application/json',
                    'accept-encoding': 'gzip, deflate, br',
                    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
                    'referer': 'http://www.sydney.edu.au/engineering/about/our-people/research-students/' + person['urlid'].replace('.', '-') + '.html',
                    'sec-fetch-mode': 'cors',
                    'sec-fetch-site': 'same-origin',
                    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36',
                    'x-requested-with': 'XMLHttpRequest',
                }
                url = 'https://www.sydney.edu.au/AcademicProfiles/interfaces/rest/getHrPerson/' + person['urlid']
                yield scrapy.Request(url, callback=self.parse_staff, headers=headers)
                url = 'https://www.sydney.edu.au/AcademicProfiles/interfaces/rest/getGrantDetails/' + person['urlid']
                yield scrapy.Request(url, callback=self.parse_staff, headers=headers)
                url = 'https://www.sydney.edu.au/AcademicProfiles/interfaces/rest/getExpertiseDetails/' + person['urlid']
                yield scrapy.Request(url, callback=self.parse_staff, headers=headers)
                url = 'https://www.sydney.edu.au/AcademicProfiles/interfaces/rest/getAuthorDetails/' + person['urlid']
                yield scrapy.Request(url, callback=self.parse_staff, headers=headers)
                url = 'https://www.sydney.edu.au/AcademicProfiles/interfaces/rest/getThesisList/' + person['urlid']
                yield scrapy.Request(url, callback=self.parse_staff, headers=headers)

    def parse_staff(self, response):
        raw_data = response.body
        data = json.loads(raw_data)
        yield data
import json
import scrapy


class StaffPubSpider(scrapy.Spider):
    name = 'staff_pub'
    allowed_domains = ['www.sydney.edu.au']
    start_urls = ['https://www.sydney.edu.au/engineering/about/our-people/academic-staff.html']
    
    def parse(self, response):
        with open('staff_id.json') as json_file:
            data = json.load(json_file)[0]['json']
            for person in data:
                print(person)
                url = 'https://www.sydney.edu.au/AcademicProfiles/interfaces/rest/getAuthorDetails/' + person['urlid']
                headers = {
                    'accept': 'application/json',
                    'accept-encoding': 'gzip, deflate, br',
                    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
                    'referer': 'http://www.sydney.edu.au/engineering/about/our-people/academic-staff/' + person['urlid'].replace('.', '-') + '.html',
                    'sec-fetch-mode': 'cors',
                    'sec-fetch-site': 'same-origin',
                    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36',
                    'x-requested-with': 'XMLHttpRequest',
                }
                yield scrapy.Request(url, callback=self.parse_staff_hr, headers=headers)

    def parse_staff_hr(self, response):
        raw_data = response.body
        data = json.loads(raw_data)
        yield data
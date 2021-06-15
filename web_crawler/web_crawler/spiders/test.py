# import scrapy
# import json

# class TestSpider(scrapy.Spider):
#     name = 'test'
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
#         yield Person(given_names=data['givenName'], surname=data['surname'], email=data['emailAddress'])

# # class TestSpider(scrapy.Spider):
# #     name = 'test'
# #     allowed_domains = ['www.sydney.edu.au']
# #     start_urls = ['http://www.sydney.edu.au/engineering/about/our-people/academic-staff/eman-mousavinejad.html']
# #     headers = {
# #         'accept': 'application/json',
# #         'accept-encoding': 'gzip, deflate, br',
# #         'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
# #         'referer': 'https://www.sydney.edu.au/engineering/about/our-people/academic-staff/eman-mousavinejad.html',
# #         'sec-fetch-mode': 'cors',
# #         'sec-fetch-site': 'same-origin',
# #         'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36',
# #         'x-requested-with': 'XMLHttpRequest',
# #     }

# #     def parse(self, response):
# #         url = 'https://www.sydney.edu.au/AcademicProfiles/interfaces/rest/getHrPerson/eman.mousavinejad'
# #         request = scrapy.Request(url, callback=self.parse_api, headers=self.headers)
# #         yield request

# #     def parse_api(self, response):
# #         raw_data = response.body
# #         data = json.loads(raw_data)
# #         yield data

# # full_header = {
# #     'authority': 'www.sydney.edu.au',
# #     'method': 'GET',
# #     'path': '/AcademicProfiles/interfaces/rest/getHrPerson/eman.mousavinejad',
# #     'scheme': 'https',
# #     'accept': 'application/json, text/javascript, */*; q=0.01',
# #     'accept-encoding': 'gzip, deflate, br',
# #     'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
# #     'cache-control': 'no-cache',
# #     'content-type': 'text/plain',
# #     'cookie': 'at_check=true; AMCVS_35B46472540D9EE20A4C98A6%40AdobeOrg=1; _hjTLDTest=1; _hjid=fe26c5e7-73b1-4cd5-a90c-9fbecbf2d723; s_cc=true; _gcl_au=1.1.1097209599.1623580026; _fbp=fb.2.1623580026353.271422002; s_ips=1219; s_tp=1371; s_ppv=sydney%253Aengineering%253Aabout%253Aour%2520people%253Aacademic%2520staff%253Aeman%2520mousavinejad%2C89%2C89%2C1219%2C1%2C1; AWSELB=5D8F8DC30A99AF31E141F5E14CB1D20040FBF446A422190E14F0FA0B0087F959FCDA85C298C2FDAEA2EA5C532B2BBDC5497FF5CAF698A8142BB0381F620336374481F137EE; AWSELBCORS=5D8F8DC30A99AF31E141F5E14CB1D20040FBF446A422190E14F0FA0B0087F959FCDA85C298C2FDAEA2EA5C532B2BBDC5497FF5CAF698A8142BB0381F620336374481F137EE; AKA_A2=A; mbox=PC#045aa7f993c74366a60140c181072941.36_0#1686880040|session#f750c1a081b8400f8106d080a74027ec#1623637100; gpv_Page=sydney%3Aengineering%3Aabout%3Aour%20people%3Aacademic%20staff%3Aeman%20mousavinejad; _hjIncludedInPageviewSample=1; _hjIncludedInSessionSample=0; AMCV_35B46472540D9EE20A4C98A6%40AdobeOrg=-1124106680%7CMCIDTS%7C18792%7CMCMID%7C87117908601149086191959278962062110363%7CMCAAMLH-1624240039%7C8%7CMCAAMB-1624240039%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1623642439s%7CNONE%7CvVersion%7C5.2.0',
# #     'pragma': 'no-cache',
# #     'referer': 'https://www.sydney.edu.au/engineering/about/our-people/academic-staff/eman-mousavinejad.html',
# #     'sec-ch-ua': '\" Not;A Brand\";v=\"99\", \"Google Chrome\";v=\"91\", \"Chromium\";v=\"91\"',
# #     'sec-ch-ua-mobile': '?0',
# #     'sec-fetch-dest': 'empty',
# #     'sec-fetch-mode': 'cors',
# #     'sec-fetch-site': 'same-origin',
# #     'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36',
# #     'x-requested-with': 'XMLHttpRequest',
# # }
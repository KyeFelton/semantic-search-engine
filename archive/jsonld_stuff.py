
def extract_faculty_school_institute(string):
    org_list = string.split(' > ')
    faculty = {
        '@id': KG_URL + org_list[0].replace(' ', '_'),
        '@type': 'Faculty',
        'name': org_list[0],
        'school': KG_URL + org_list[1].replace(' ', '_')
    }
    school = {
        '@id': KG_URL + org_list[1].replace(' ', '_'),
        '@type': 'School',
        'name': org_list[1]
    }
    institute = None
    if len(org_list) > 2 and not org_list[2] in org_list[1]:
        institute = {
            '@id': KG_URL + org_list[2].replace(' ', '_'),
            '@type': 'Institute',
            'name': org_list[2]
        }
        school['institute'] = KG_URL + org_list[2].replace(' ', '_')

    return faculty, school, institute
    
        # with open('../scraped_data/people.json') as f:
        #     data = json.loads(f.read())

        # with open('./temp.json', 'w') as f:
        #     f.write(json.dumps(data[:20]))
        
        # Removing data approaches

        # # Approach 1
        # person['getHrPerson'].pop('uid')
        # person['getHrPerson'].pop('emailSecuirtyLevel')
        # person['getHrPerson'].pop('havingCV')
        
        # # Approach 2
        # person_jsonld = {
        #     'id': person['id'],
        #     'fullName': person['getGrPerson']['fullName'],
        #     'givenName': person['getGrPerson']['givenName'],
        #     'surName': person['getGrPerson']['surName'],
        # }

        # # Approach 3
        # person_details = {}
        # keys = ['fullName', 'givenName', 'surname', 'salutation', 'emailAddress', ]
        # new_person = (person['getHrPerson'], keys)
        # print(new_person)

#         def entity(type, label):

# def copy_elements(json, keys):
#     new_json = {}
#     for key in keys:
#         new_json[key] = json[key]
#     return new_json

# def get_hr_details(person):
#     details = {}
#     keys = [
#         'fullName',
#         'givenName',
#         'surname',
#         'salutation',
#         'jobTitle',
#         'emailAddress',
#         'postalAddress',
#         'phoneNumber',
#         'faxNumber',
#         'mobilePhoneNumber'
#     ]
#     details.update(copy_elements(person, keys))
#     return details

# old_context = {
#     '@context': {
#         'Student': ONT_URL + 'Student',
#         'AcademicStaff': ONT_URL + 'AcademicStaff',
#         'Faculty': ONT_URL + 'Faculty',
#         'School': ONT_URL + 'School',
#         'Institute': ONT_URL + 'Institute',
#         'Building': ONT_URL + 'Building',
#         'Thesis': ONT_URL + 'Thesis',
#         'Publication': ONT_URL + 'Publication',
#         'People': ONT_URL + 'People',
#         'Grant': ONT_URL + 'Grant',
#         'Collaboration': ONT_URL + 'Collaboration',
#         'ExternalAssociate': ONT_URL + 'ExternalAssociate',
#     }
# }



    # url = f'https://www.sydney.edu.au/apps/maps/buildings.php?format=json&campus={campus_id}%2C'
    # yield scrapy.Request(url, callback=self.parse_data, headers=headers, meta={'type': 'building'})

    # def parse(self, response):
    #     headers = self.headers
    #     url = 'https://www.sydney.edu.au/apps/maps/buildings.php?format=json&campus=1%2C12%2C'
    #     yield scrapy.Request(url, callback=self.parse_data, headers=headers, meta={'type': 'building'})
    #     # url = 'https://www.sydney.edu.au'
    #     # yield scrapy.Request(url, callback=self.parse_data, headers=headers, meta={'type': 'amenity'})


    # def parse_campus(self, response):
    #     if response.body:
    #         headers = self.headers

    #         for campus_id in response.body['areas'][0]['campuses']:
    #             url = 
    #             yield scrapy.Request(url, callback=self.parse_data, headers=headers, meta={'type': 'amenity'})
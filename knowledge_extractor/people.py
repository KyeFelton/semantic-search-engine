import json

CONTEXT = 'http://www.semanticweb.org/kyefelton/ontologies/2021/4/usyd-ontology-v2',

hr_details = [
    'fullName',
    'givenName',
    'surname',
    'salutation',
    'jobTitle',
    'primaryFacultyAffiliation',
    'emailAddress',
    'postalAddress',
    'phoneNumber',
    'faxNumber',
    'mobilePhoneNumber'
]

def copy_elements(json, keys):
    new_json = {}
    for key in keys:
        new_json[key] = json[key]
    return new_json


if __name__ == '__main__':

    with open('./people.json') as f:
        data = json.loads(f.read())

    jsonld = []
    
    for element in data:
        person = {}
        person['@context'] = CONTEXT
        if element.contains('getThesisList'):
            person['@type'] = 'Student'
        elif element.contains('getCollaborator'):
            person['@type'] = 'AcademicStaff'
        else:
            person['@type'] = 'Person'
        person['id'] = person['id'] 
        person.update(copy_elements(person['getHrPerson'], hr_details))
        
        print(person)
        
        
        
        



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
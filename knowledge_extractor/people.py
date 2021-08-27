import json

CONTEXT = 'http://www.semanticweb.org/kyefelton/ontologies/2021/4/usyd-ontology',

def entity(type, label):


def copy_elements(json, keys):
    new_json = {}
    for key in keys:
        new_json[key] = json[key]
    return new_json

def get_hr_details(person):
    details = {}
    keys = [
        'fullName',
        'givenName',
        'surname',
        'salutation',
        'jobTitle',
        'emailAddress',
        'postalAddress',
        'phoneNumber',
        'faxNumber',
        'mobilePhoneNumber'
    ]
    details.update(copy_elements(person, keys))
    return details



def get_affiliations(person):
    primary_aff = {}
    primary_aff_str = person['primaryFacultyAffiliation']
    primary_aff_list = primary_aff_str.split(' > ')
    faculty = {
        '@type': 'Faculty',
        'name': primary_aff_list[0],
        'school': primary_aff_list[1]
    }
    school = {
        '@type': 'School',
        'name': primary_aff_list[1]
    }
    if primary_aff_list[1] != primary_aff_list[2]:
        institute = {
            '@type': 'Institute',
            'name': primary_aff_list[2]
        }
        school['institute'] = primary_aff_list[2]
        primary_aff = institute
    else:
        primary_aff = school

    return primary_aff

if __name__ == '__main__':

    with open('./people.json') as f:
        data = json.loads(f.read())

    jsonld = []
    
    for element in data:
        
        person = {}
        person['@context'] = CONTEXT
        if 'getThesisList' in element:
            person['@type'] = 'Student'
        elif 'getCollaborator' in element:
            person['@type'] = 'AcademicStaff'
        else:
            person['@type'] = 'Person'

        person['id'] = element['id'] 
        person.update(get_hr_details(element['getHrPerson']))

        person['primaryAffilitation'] = get_affiliations(element['primaryFacultyAffilition'])
        person['affiliation'] = []
        for other_aff in person['affiliationList']:
            person['affiliation'].append(get_affiliations(other_aff))        
        jsonld.append(person)
    
    with open('./jsonld.json', 'w') as f:
        f.write(json.dumps(jsonld))
        
        
        
        



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
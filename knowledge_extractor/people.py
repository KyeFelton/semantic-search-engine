import hashlib
import json

ONT_URL = 'http://www.sydney.edu.au/ontology/'
KG_URL = 'http://www.sydney.edu.au/kg/'
CONTEXT = {
    'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
    'owl': 'http://www.w3.org/2002/07/owl#',
    'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
    '@vocab': ONT_URL,
    'stardog': 'tag:stardog:api:',
    'xsd': 'http://www.w3.org/2001/XMLSchema#'
}

kg = []

# Make argument names consistent among functions
# Don't forget to perform reasoning to ensure knowledge graph is correct

# Comment here
def get_id_from_str(string):
    m = hashlib.md5()
    m.update(string.encode('utf-8'))
    return m.hexdigest()[0:10]


# Comment here
def create_faculty_school(string):
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
    kg.extend([ faculty, school ])
    return faculty['@id'], school['@id']


# Comment here
def create_building(label):
    building = {
        '@id': KG_URL + label.split(' - ', 1)[0],
        'name': label.split(' - ', 1)[1]
    }
    kg.append(building)
    return building['@id']


# Comment here
def create_person(pid, typ, hr_details, exp_details):
    person = {}
    person['@id'] = KG_URL + pid

    if typ == 'academic-staff':
        person['@type'] = 'AcademicStaff'
    elif typ == 'research-student':
        person['@type'] = 'ResearchStudent'
    else:
        person['@type'] = 'Person'

    person.update(hr_details)
    person.update(exp_details)

    if hr_details['building']:
        person['building'] = create_building(hr_details['building'])

    affiliation_list = []
    for affiliation in hr_details['affiliationList']:
        faculty_id, school_id = create_faculty_school(affiliation)
        affiliation_list.append({'@id': school_id})
    person['affilitation'] = affiliation_list
    del person['affiliationList']

    kg.append(person)


# Comment here
def create_theses(pid, thesis_list):
    for thesis in thesis_list:
        tid = get_id_from_str(thesis['thesisTitle'])       
        supervisor_id_list = []
        for supervisor in thesis['supervisors']:
            person = {
                '@id': KG_URL + supervisor['urlId'],
                '@type': 'AcademicStaff',
                'givenName': supervisor['givenName'],
                'surname': supervisor['surName']
            }
            kg.append(person)
            supervisor_id_list.append(person['@id'])
        kg.append({
            '@id': KG_URL + tid,
            '@type': 'Thesis',
            'thesisDegree': thesis['thesisDegree'],
            'thesisAbstract': thesis['thesisAbstract'],
            'supervisor': supervisor_id_list
        })


# Comment here
def create_publications(pid, publications):
    for publication in publications:
        publication['@id'] = KG_URL + get_id_from_str(publication['publicationTitle'])
        publication['@type'] = 'Publication'
        del publication['authors'] # don't have @id for each author, so removing to avoid inconsistencies
        publication['author'] = KG_URL + pid
        kg.append(publication)
    
# Comment here
def create_grants(pid, grants):
    for grant in grants:
        grant['@id'] = KG_URL + get_id_from_str(grant['title'])
        grant['@type'] = 'Grant',
        grant['author'] = KG_URL + pid
        kg.append(grant)


# Comment here
def create_collaborations(pid, collaborations):
    for collaboration in collaborations:
        kg.append({
            '@id': KG_URL + collaboration['institution'].replace(' ', '_'),
            '@type': 'ExternalOrganisation',
            'country': collaboration['countryTitle']
        })
        kg.append({
            '@id': KG_URL + get_id_from_str(collaboration['relationshipdetails']),
            '@type': 'Collaboration',
            'staff': KG_URL + pid,
            'relationship': collaboration['relationshipdetails'],
            'comments': collaboration['comments']
        })


if __name__ == '__main__':

    # with open('../scraped_data/people.json') as f:
    #     data = json.loads(f.read())

    # with open('./people', 'w') as f:
    #     f.write(json.dumps(data[0:20]))

    with open('./people.json') as f:
        data = json.loads(f.read())
    
    for person in data:
        pid, typ = person['id'], person['type']

        create_person(pid, typ, person['getHrPerson'], person['getExpertiseDetails'])
        create_theses(pid, person['getThesisList'])
        create_grants(pid, person['getGrantDetails']['grants'])
        create_collaborations(pid, person['getCollaborator']['collaborations'])
        create_publications(pid, person['getAuthorDetails']['researchPublications']) # , person['getPublishingActiveAuthor'], person['getAuthorsNewKeywords'], person['getBookSellingLinks'])
        # create_supervisors(pid, person['getHonoursSupervisor'], person['getSupervisedStudents'], person['getResearchSupervisor'])

    with open('./people_kg.json', 'w') as f:
        f.write(json.dumps({ 
            '@context': CONTEXT,
            '@graph': kg 
        }))

from builders.builder import Builder

from collections import abc
import datetime

class PersonBuilder(Builder):

    def __init__(self, ifile):
        super().__init__(ifile)
        self.context.update({
            # 'dateCommenced': {
            #     '@type': 'xsd:dateTime'
            # },
            # 'endDate': {
            #     '@type': 'xsd:dateTime'
            # },
            # 'totalAmount': {
            #     '@type': 'xsd:integer'
            # },
            # 'profileUrl': {
            #     '@type': 'xsd:anyURI'
            # }
        })


    def build(self, data): 
        
        # For each person       
        for person in data:
            
            # Create a url
            person['@id'] = self.make_url('person', person['id'])
            del person['id']
            # Create a type
            if person['type'] == 'academic-staff':
                person['@type'] = 'AcademicStaff'
            elif person['type'] == 'research-student':
                person['@type'] = 'ResearchStudent'
            del person['type']

            # Flatten dict structure
            for k in ['getHrPerson', 'getExpertiseDetails']:
                if k in person and person[k]:
                    person.update(person[k])
                    del person[k]
            
            # Remove unnecessary data
            if 'emailSecurityLevel' in person: del person['emailSecurityLevel']
            if 'primaryJobType' in person: del person['primaryJobType']
            if 'staffId' in person: del person['staffId']
            if 'surName' in person: del person['surName']
            if 'urlId' in person: del person['urlId']
            
            # Remove empty key value pairs
            delete = []
            for k, v in person.items():
                if self.empty_value(v):
                    delete.append(k)
            for k in delete:
                del person[k]
            
            # Establish building location
            if 'building' in person:
                person['building'] = { '@id': self.make_url('building', person['building'].split(' - ', 1)[0]) }

            # Establish primary faculty or school affiliation
            if 'primaryFacultyAffiliation' in person:
                person['primaryAffiliation'] = self.find_faculty_school(person['primaryFacultyAffiliation'])
                del person['primaryFacultyAffiliation']

            # Establish faculty and school affiliations
            person['affiliation'] = []
            if 'affiliationList' in person:    
                for affiliation in person['affiliationList']:
                    person['affiliation'].append(self.find_faculty_school(affiliation))
                del person['affiliationList']
            
            # Establish other affiliations
            if 'getCentreListForStaff' in person:
                for centre in person['getCentreListForStaff']:
                    org = {}
                    org['@id'] = self.make_url('organisation', centre['name'].replace(' ', '_'))
                    org['@type'] = 'Organisation'
                    person['affiliation'].append({ '@id': org['@id'] })
                del person['getCentreListForStaff']
            
            # Remove jobs - can create these nodes later if time permits
            if 'hrJobList' in person: 
                del person['hrJobList']
            
            # Add person to the kg
            self.add_node(person)

            # If there are theses
            if 'getThesisList' in person:
                # For each thesis
                for thesis in person['getThesisList']:  
                    
                    # Create the url
                    thesis['@id'] = self.make_url('thesis', self.get_id_from_str(thesis['thesisTitle']))
                    # Create the type
                    thesis['@type'] = 'Thesis'
                    
                    # Establish the author
                    thesis['author'] = { "@id": person['@id'] }

                    # Establish the supervisors
                    thesis['supervisor'] = []
                    for supervisor in thesis['supervisors']:
                        supervisor['@id'] = self.make_url('person', supervisor['urlId'])
                        supervisor['@type'] = 'AcademicStaff'
                        self.add_node(supervisor)
                        thesis['supervisor'].append({ "@id": supervisor['@id'] })
                    del [thesis['supervisors']]
                    
                    # Add thesis to kg
                    self.add_node(thesis)

                del person['getThesisList']

            # If there are publications
            if 'getAuthorDetails' in person:
                # For each publication
                for pub in person['getAuthorDetails']['researchPublications']:
                    
                    # Create the url
                    pub['@id'] = self.make_url('publication', self.get_id_from_str(pub['publicationTitle']))
                    # Create the type
                    pub['@type'] = 'Publication'
                    
                    # Establish the author
                    pub['author'] = [ { "@id": person['@id'] } ]
                    
                    # Remove empty key value pairs
                    delete = []
                    for k, v in pub.items():
                        if self.empty_value(v):
                            delete.append(k)
                    for k in delete:
                        del pub[k]

                    pub['authorString'] = ''
                    for author in pub['authors']:
                        if author['surname'] and author['givenName']:
                            pub['authorString'] += author['givenName'] + ' ' + author['surname'] + ', '
                    
                    # Remove authors - unable to identify with urlid
                    del pub['authors']

                    # Add publication to kg
                    self.add_node(pub)
                
                del person['getAuthorDetails']

            # If there are grants
            if 'getGrantDetails' in person: 
                # For each grant
                for grant in person['getGrantDetails']['grants']:

                    # Create the url
                    grant['@id'] = self.make_url('grant', self.get_id_from_str(grant['title']))
                    # Create the type
                    grant['@type'] = 'Grant'

                    # Establish the author
                    grant['author'] = { '@id': person['@id'] }

                    # Add grant to kg
                    self.add_node(grant)

                del person['getGrantDetails']

            # If there are collaborations
            if 'getCollaborator' in person:
                # For each collaboration
                for collab in person['getCollaborator']['collaborations']:
                    
                    # Create an external organistion
                    org = {}
                    # Create the url
                    org['@id'] = self.make_url('organisation', collab['institution'].replace(' ', '_'))
                    # Create the type
                    org['@type'] = 'ExternalOrganisation'
                    # Establish the country
                    org['country'] = collab['countryTitle']
                    # Add external organisation to kg
                    self.add_node(org)
            
                    # Create the collaboration url
                    collab['@id'] = self.make_url('collaboration', self.get_id_from_str(collab['relationshipdetails']))
                    # Create the type
                    collab['@type'] = 'Collaboration'
                    # Establish the external organisation
                    collab['organisation'] = { '@id': org['@id'] }
                    # Establish the staff
                    collab['staff'] = { '@id': person['@id'] }
                    
                    # Remove duplicate data
                    del collab['countryTitle']
                    del collab['country_id']
                    
                    # Add collaboration to kg
                    self.add_node(collab)

                del person['getCollaborator']

            # Missing info
            missing_info = ['getPublishingActiveAuthor', 'getAuthorsNewKeywords', 'getBookSellingLinks', 'getHonoursSupervisor', 'getSupervisedStudents', 'getResearchSupervisor']
            for i in missing_info:
                if i in person:
                    del[person[i]]

    def find_faculty_school(self, string):
        # Split the string into the faculty name and school name
        org_list = string.split(' > ')
        # Get the faculty url from the faculty name
        fac_url = self.make_url('organisation', org_list[0].replace(' ','_'))
        # Create the faculty node if new, else just return the url
        if fac_url not in self.urls:
            faculty = {}
            faculty['@id'] = fac_url
            faculty['@type'] = 'Faculty'
            faculty['name'] = org_list[0]
            self.urls.add(fac_url)
        else:
            faculty = { '@id': fac_url }

        # If there is a school name, get it, else return the faculty
        if len(org_list) > 1:
            # Get the school url from the school name
            sch_url = self.make_url('organisation', org_list[1].replace(' ','_'))
            # Create the school node if new, else just return the url
            if sch_url not in self.urls:
                school = {}
                school['@id'] = sch_url
                school['@type'] = 'Department'
                school['name'] = org_list[1]
                school['faculty'] = faculty
                self.urls.add(sch_url)
                return school
            else:
                return { '@id': sch_url }
        else:
            return faculty


    # Find all the unit codes in a string and return their urls
    def find_units(self, text):
        if type(text) is not str:
            return None
        unit_codes = re.findall('\\b[A-Z]{4}[0-9]{4}', text)
        unit_urls = [ { '@id': self.make_url('unit', code) } for code in unit_codes ]
        return unit_urls if len(unit_urls) > 0 else None

    # Check if value is empty
    def empty_value(self, v):
        if v is None:
            return True
        elif type(v) is list and len(v) < 0:
            return True
        elif v is False:
            return True
        elif type(v) is str and v == '':
            return True
        else:
            return False
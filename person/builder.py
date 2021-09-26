import re
import spacy

from base.builder import Builder


class PersonBuilder(Builder):
    ''' JSON-LD KG Builder for Person entities '''

    def __init__(self, root_dir):
        '''Initialises the KG builder.
        '''
        self.name = 'person'
        super().__init__(root_dir)

    def _parse(self):
        '''Builds the KG.'''

        nlp = spacy.load("en_core_web_sm")

        # For each person
        for homepage, person in self.data.items():

            # Flatten dict structure
            for k in ['getHrPerson', 'getExpertiseDetails']:
                if k in person and person[k]:
                    person.update(person[k])
                    del person[k]

            # Create person entity
            person['@id'] = self._make_uri(person['id'])
            del person['id']
            if person['type'] == 'academic-staff':
                person['@type'] = 'AcademicStaff'
            elif person['type'] == 'research-student':
                person['@type'] = 'ResearchStudent'
            del person['type']
            if 'fullName' in person:
                person['rdfs:label'] = person['fullName']
            person['homepage'] = homepage
            person['association'] = []

            # Remove unwanted data
            unwanted = ['getPublishingActiveAuthor', 'getAuthorsNewKeywords', 'getHonoursSupervisor', 'getSupervisedStudents', 'getResearchSupervisor', 'profileUrl',
                        'emailSecurityLevel', 'primaryJobType', 'staffId', 'surName', 'urlId', 'urlid', 'havingPhoto', 'havingCV', 'mediaMobilePublic', 'hrJobList', 'mediaMobilePublic']
            for i in unwanted:
                if i in person:
                    del[person[i]]

            # Establish building location
            if 'building' in person:
                person['building'] = { '@id': self._make_uri(person['building'].split(' - ', 1)[0]) }

            # Establish primary faculty or school affiliation
            if 'primaryFacultyAffiliation' in person:
                person['primaryAffiliation'] = self._find_faculty_school(person['primaryFacultyAffiliation'])
                del person['primaryFacultyAffiliation']

            # Establish faculty and school affiliations
            person['affiliation'] = []
            if 'affiliationList' in person:
                for affiliation in person['affiliationList']:
                    person['affiliation'].append(self._find_faculty_school(affiliation))
                del person['affiliationList']

            # Establish other affiliations
            if 'getCentreListForStaff' in person:
                for centre in person['getCentreListForStaff']:
                    org = {}
                    org['@id'] = self._make_uri(centre['name'])
                    org['@type'] = 'Organisation'
                    org['rdfs:label'] = centre['name']
                    self._add_entity(org)
                    person['affiliation'].append({'@id': org['@id']})
                del person['getCentreListForStaff']

            # Establish associations
            if 'associations' in person:
                doc = nlp(person['associations'])
                for ent in doc.ents:
                    if ent.label_ == 'ORG':
                        org = {}
                        org['@id'] = self._make_uri(ent.text)
                        org['@type'] = 'Organisation'
                        org['rdfs:label'] = ent.text
                        self._add_entity(org)
                        person['association'].append({ '@id': org['@id'] })
                #person['associationStr'] = person['associations']
                del person['associations']
            
            # If there are theses
            if 'getThesisList' in person:
                # For each thesis
                for thesis in person['getThesisList']:

                    # Create thesis entity
                    thesis['@id'] = self._make_uri(thesis['thesisTitle'])
                    thesis['@type'] = 'Thesis'
                    thesis['rdfs:label'] = thesis['thesisTitle']

                    # Establish the author
                    thesis['author'] = {"@id": person['@id']}

                    # Establish the supervisors
                    thesis['supervisor'] = []
                    for supervisor in thesis['supervisors']:
                        supervisor['@id'] = self._make_uri(supervisor['urlId'])
                        supervisor['@type'] = 'AcademicStaff'
                        del supervisor['staffId']
                        del supervisor['urlId']
                        del supervisor['surName']
                        thesis['supervisor'].append(supervisor)
                    del [thesis['supervisors']]

                    # Add thesis to kg
                    self._add_entity(thesis)

                del person['getThesisList']

            # If there are publications
            if 'getAuthorDetails' in person: 
                if 'researchPublications' in person['getAuthorDetails']:
                
                    # For each publication
                    for pub in person['getAuthorDetails']['researchPublications']:

                        # Create publication entity
                        if 'doi' in pub:
                            pub['doi'] = pub['doi'].replace(' ', '')
                            pub['homepage'] = pub['doi']
                            pub['@id'] = self._make_uri(pub['doi'])
                        else:
                            pub['@id'] = self._make_uri(pub['publicationTitle'])
                        pub['@type'] = 'Publication'
                        pub['rdfs:label'] = pub['publicationTitle']

                        # Establish the author
                        pub['author'] = [{"@id": person['@id']}]

                        # Establish other authors
                        pub['authorString'] = ''
                        for author in pub['authors']:
                            if 'surname' in author and 'givenName' in author:
                                pub['authorString'] += author['givenName'] + ' ' + author['surname'] + ', '
                        del pub['authors']

                        # Remove unwanted data
                        unwanted = ['authorTruncated', 'output1Code', 'output2Code']
                        for i in unwanted:
                            if i in person:
                                del[person[i]]

                        # Add publication to kg
                        self._add_entity(pub)

                del person['getAuthorDetails']

            # If there are selling books
            if 'getBookSellingLinks' in person:
                # For each book
                for book in person['getBookSellingLinks']:

                    # Create book entity
                    if 'bookCoverUrl' in person:
                        url = book['bookCoverUrl'].replace(' ', '')
                        book['@id'] = self._make_uri(url)
                        book['homepage'] = url
                        del book['bookCoverUrl']
                    else:
                        book['@id'] = self._make_uri(book['bookName'])
                    book['@type'] = 'Book'
                    book['rdfs:label'] = book['bookName']

                    # Establish the author
                    book['author'] = {'@id': person['@id']}

                    # Establish currently sold
                    book['selling'] = True

                    # Remove unnecessary data
                    unwanted = ['publicationId', 'output1Code', 'output2Code', 'bookCoverFilename']
                    for i in unwanted:
                        if i in book:
                            del[book[i]]

                    # Add book to kg
                    self._add_entity(book)

                del person['getBookSellingLinks']

            # If there are grants
            if 'getGrantDetails' in person:
                if 'grants' in person['getGrantDetails']:
                    # For each grant
                    for grant in person['getGrantDetails']['grants']:

                        # Create grant entity
                        grant['@id'] = self._make_uri(grant['title'])
                        grant['@type'] = 'Grant'
                        grant['rdfs:label'] = grant['title']

                        # Establish the author
                        grant['grantee'] = {'@id': person['@id']}

                        # Add grant to kg
                        self._add_entity(grant)

                del person['getGrantDetails']

            # If there are collaborations
            if 'getCollaborator' in person:
                if 'collaborations' in person['getCollaborator']:
                
                    person['collaboration'] = []                    

                    # For each collaboration
                    for collab in person['getCollaborator']['collaborations']:

                        # Create external organisation entity
                        org = {}
                        org['@id'] = self._make_uri(collab['institution'])
                        org['@type'] = 'ExternalOrganisation'
                        org['rdfs:label'] = collab['institution']
                        org['country'] = collab['countryTitle']

                        # Add external organisation to kg
                        self._add_entity(org)

                        # Create collaboration blank node
                        node = {}
                        node['organisation'] = {'@id': org['@id']}
                        node['details'] = collab['relationshipdetails']
                        person['collaboration'].append(node)
                
                del person['getCollaborator']

            # If there are teaching areas
            if 'teachingareas' in person:

                # Establish units taught
                person['unitsTaught'] = self._find_units(person['teachingareas'])
                del person['teachingareas']
            
            # If there are urls
            if 'urls' in person:
                for i in range(0, len(person['urls'])):

                    # Establish association to external org
                    url = person['urls'][i].replace(' ', '')
                    domain = url.split('/')[2]
                    if 'sydney.edu.au' not in domain:
                        org = {}
                        org['@id'] = self._make_uri(person['urlNames'][i])
                        org['@type'] = 'ExternalOrganisation'
                        org['rdfs:label'] = person['urlNames'][i]
                        org['homepage'] = url
                        self._add_entity(org)
                        person['association'].append({ '@id': org['@id'] })
                
                del person['urlNames']
                del person['urls']
            
            # If there is media
            if 'media' in person:

                # Pass for now
                pass

            # If there is others
            if 'others' in person:

                # Ignore for now
                del person['others']


            # Add person to the kg
            self._add_entity(person)

    def _find_faculty_school(self, heirarchy):
        '''Finds a faculty and school from an organisation heirarchy string.

        Args:
            heirarchy (str): The string containing the faculty and school heirarchy. 
                E.g. 'Faculty of Engineering > School of Computer Science'

        Returns 
            (str): The school uri if found, otherwise the faculty uri
        '''
        # Split the string into the faculty name and school name
        org_list = heirarchy.split(' > ')

        # Create faculty entity
        faculty = {}
        faculty['@id'] = self._make_uri(org_list[0])
        faculty['@type'] = 'Faculty'
        faculty['rdfs:label'] = org_list[0]

        # Add faculty to the KG
        self._add_entity(faculty, False)

        # If there is a school
        if len(org_list) > 1:

            # Create school entity
            school = {}
            school['@id'] = self._make_uri(org_list[1])
            school['@type'] = 'Department'
            school['rdfs:label'] = org_list[1]

            # Establish the factory
            school['faculty'] = faculty

            # Add school to the KG
            self._add_entity(school, False)

            return {'@id': school['@id']}
        else:
            return {'@id': faculty['@id']}

    def _find_units(self, text):
        '''Returns the units found within some text.

        Args:
            text (str): The text to be inspected.

        Returns
            (list): List of unit uris found within the text, otherwise None
        '''
        if type(text) is not str:
            return []
        unit_codes = re.findall('\\b[A-Z]{4}[0-9]{4}', text)
        unit_uris = [{'@id': self._make_uri(code)} for code in unit_codes]
        return unit_uris if len(unit_uris) > 0 else []
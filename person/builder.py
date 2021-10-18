import json
import re
import spacy

from base.builder import Builder


class PersonBuilder(Builder):
    ''' JSON-LD KG Builder for Person entities '''

    def __init__(self, root_dir):
        '''Initialises the KG builder.
        '''
        self.name = 'person'
        with open(f'{root_dir}/synonyms.json') as f:
            self.synonyms = json.loads(f.read())
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
                person['@type'] = 'Staff'
            elif person['type'] == 'research-student':
                person['@type'] = 'Student'
            del person['type']
            if 'fullName' in person:
                person['rdfs:label'] = [person['fullName']]
                person['name'] = person['fullName']
                if 'salutation' in person:
                    person['rdfs:label'].append(f'{person["salutation"]} {person["fullName"]}')
            elif 'firstName' in person and 'surname' in person:
                person['name'] = person['firstName'] + person['surname']
                person['rdfs:label'] = [person['firstName'] + person['surname']]
                if 'salutation' in person:
                    person['rdfs:label'].append(f'{person["salutation"]} {person["name"]}')
            else:
                person['name'] = None
                person['rdfs:label'] = None
            person['homepage'] = homepage
            person['website'] = homepage
            if 'blurb' in person:
                person['summary'] = person['blurb']
            elif 'bio' in person:
                person['summary'] = person['bio']
            else:
                person['summary'] = ''
            person['association'] = []

            # Remove unwanted data
            unwanted = ['getPublishingActiveAuthor',
                        'getAuthorsNewKeywords',
                        'getHonoursSupervisor',
                        'getSupervisedStudents',
                        'getResearchSupervisor',
                        'profileUrl',
                        'emailSecurityLevel',
                        'primaryJobType',
                        'staffId',
                        'surName',
                        'urlId',
                        'urlid',
                        'havingPhoto',
                        'havingCV',
                        'mediaMobilePublic',
                        'hrJobList',
                        'mediaMobilePublic']
            for i in unwanted:
                if i in person:
                    del [person[i]]

            # Establish building location
            if 'building' in person:
                person['building'] = {'@id': self._make_uri(person['building'].split(' - ', 1)[0])}

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
                    org = self._make_entity(uri=centre['name'],
                                            typ='Centre',
                                            name=centre['name'],
                                            homepage=None,
                                            summary='')
                    self._add_entity(org)
                    person['affiliation'].append({'@id': org['@id']})
                del person['getCentreListForStaff']

            # Establish associations
            if 'associations' in person:
                # TODO: Improve the accuracy
                # doc = nlp(person['associations'])
                # for ent in doc.ents:
                #     if ent.label_ == 'ORG':
                #         org = self._make_entity(uri=ent.text,
                #                                 typ='Organisation',
                #                                 name=ent.text,
                #                                 homepage=None,
                #                                 summary='')
                #         self._add_entity(org)
                #         person['association'].append({'@id': org['@id']})
                # person['associationStr'] = person['associations']
                del person['associations']

            # If there are theses
            if 'getThesisList' in person:
                # For each thesis
                for thesis in person['getThesisList']:

                    # Create thesis entity
                    if 'thesisAbstract' not in thesis:
                        summary = f'Author: {person["name"]}'
                    else:
                        summary = thesis['thesisAbstract']
                    entity = self._make_entity(uri=thesis['thesisTitle'],
                                               typ='Thesis',
                                               name=thesis['thesisTitle'],
                                               homepage=None,
                                               summary=summary)
                    thesis.update(entity)
                    # Establish the author
                    thesis['author'] = {"@id": person['@id']}

                    # Establish the supervisors
                    thesis['supervisor'] = []
                    for supervisor in thesis['supervisors']:
                        supervisor['@id'] = self._make_uri(supervisor['urlId'])
                        supervisor['@type'] = 'Staff'
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
                            pub['@id'] = self._make_uri(pub['doi'])
                            pub['homepage'] = pub['doi']
                            pub['website'] = pub['doi']
                        else:
                            pub['@id'] = self._make_uri(pub['publicationTitle'])
                            pub['homepage'] = None
                            pub['website'] = None
                        pub['@type'] = 'Publication'
                        pub['name'] = pub['publicationTitle']
                        pub['rdfs:label'] = pub['publicationTitle']
                        pub['summary'] = ''

                        # Establish the author
                        pub['author'] = [{"@id": person['@id']}]

                        # Establish other authors
                        pub['authorString'] = ''
                        for author in pub['authors']:
                            if 'surname' in author and 'givenName' in author:
                                pub['authorString'] += author['givenName'] + ' ' + author['surname'] + ', '
                        del pub['authors']
                        pub['authorString'] = pub['authorString'].strip()
                        if len(pub['authorString']) > 0 and pub['authorString'][-1] == ',':
                            pub['authorString'] = pub['authorString'][:-1]



                        pub['summary'] = f'Authors: {pub["authorString"]}'
                        if 'publicationDate' in pub:
                            pub['summary'] += f'; Year: {pub["publicationDate"]}'
                        elif 'conferenceYear' in pub:
                            pub['summary'] = f'; Year: {pub["conferenceYear"]}'

                        # Remove unwanted data
                        unwanted = ['authorTruncated', 'output1Code', 'output2Code']
                        for i in unwanted:
                            if i in pub:
                                del [pub[i]]

                        # Add publication to kg
                        self._add_entity(pub)

                del person['getAuthorDetails']

            # If there are selling books
            if 'getBookSellingLinks' in person:
                # For each book
                for book in person['getBookSellingLinks']:

                    # Create book entity
                    if 'bookCoverUrl' in book:
                        url = book['bookCoverUrl'].replace(' ', '')
                        book['@id'] = self._make_uri(url)
                        book['homepage'] = url
                        book['website'] = url
                        del book['bookCoverUrl']
                    else:
                        book['@id'] = self._make_uri(book['bookName'])
                        book['homepage'] = None
                        book['website'] = None
                    book['@type'] = 'Book'
                    book['name'] = book['bookName']
                    book['rdfs:label'] = book['bookName']
                    book['summary'] = ''

                    # Establish the author
                    book['author'] = {'@id': person['@id']}

                    # Establish currently sold
                    book['selling'] = True

                    # Remove unnecessary data
                    unwanted = ['publicationId', 'output1Code', 'output2Code', 'bookCoverFilename']
                    for i in unwanted:
                        if i in book:
                            del [book[i]]

                    # Add book to kg
                    self._add_entity(book)

                del person['getBookSellingLinks']

            # If there are grants
            if 'getGrantDetails' in person:
                if 'grants' in person['getGrantDetails']:
                    # For each grant
                    for grant in person['getGrantDetails']['grants']:
                        # Create grant entity
                        summary = '' if 'type' not in grant else grant['type']
                        entity = self._make_entity(uri=grant['title'],
                                                   typ='Grant',
                                                   name=grant['title'],
                                                   homepage=None,
                                                   summary=summary)
                        grant.update(entity)
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
                        # Create collaboration blank node
                        col = self._make_entity(uri=collab['institution'] + collab['relationshipdetails'],
                                                typ='Collaboration',
                                                name=collab['institution'],
                                                homepage=None,
                                                summary=collab['relationshipdetails'])
                        person['collaboration'].append({'@id': col['@id']})

                        # Add external organisation to kg
                        self._add_entity(col)

                        # Create external organisation entity
                        org = self._make_entity(uri=collab['institution'],
                                                typ='External',
                                                name=collab['institution'],
                                                homepage=None,
                                                summary=collab['countryTitle'])
                        org['collaboration'] = {'@id': col['@id']}

                        # Add external organisation to kg
                        self._add_entity(org)

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
                        org = self._make_entity(uri=person['urlNames'][i],
                                                typ='External',
                                                name=person['urlNames'][i],
                                                homepage=None,
                                                website=url,
                                                summary=None)
                        self._add_entity(org)
                        person['association'].append({'@id': org['@id']})

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

    def _find_faculty_school(self, hierarchy):
        '''Finds a faculty and school from an organisation hierarchy string.

        Args:
            hierarchy (str): The string containing the faculty and school hierarchy.
                E.g. 'Faculty of Engineering > School of Computer Science'

        Returns 
            (str): The school uri if found, otherwise the faculty uri
        '''
        # Split the string into the faculty name and school name
        org_list = hierarchy.split(' > ')

        # Create faculty entity
        fac_url = ''
        fac_name = org_list[0]
        for k, v in self.synonyms['faculty'].items():
            if fac_name in v:
                fac_url = k
                break
        if fac_url == '':
            print(f'Unable to find faculty: {fac_name}')
            return None
        faculty = self._make_entity(uri=fac_url,
                                    typ='Faculty',
                                    name=fac_name,
                                    homepage=fac_url,
                                    summary=None)
        # Add faculty to the KG
        self._add_entity(faculty, False)

        # If there is a school
        if len(org_list) > 1:

            # Create department entity
            dept_url = ''
            dept_name = org_list[1]
            for k, v in self.synonyms['department'].items():
                if dept_name in v:
                    dept_url = k
            if dept_url != '':
                dept = self._make_entity(uri=dept_url,
                                         typ='Department',
                                         name=dept_name,
                                         homepage=dept_url,
                                         summary=None)
                # Establish the factory
                dept['faculty'] = faculty

                # Add school to the KG
                self._add_entity(dept, False)

                return {'@id': dept['@id']}

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
        for code in unit_codes:
            unit = self._make_entity(uri=code,
                                     typ='Unit',
                                     name=None,
                                     label=code,
                                     homepage=None,
                                     summary=None)
            self._add_entity(unit)
        unit_uris = [{'@id': self._make_uri(code)} for code in unit_codes]
        return unit_uris if len(unit_uris) > 0 else []

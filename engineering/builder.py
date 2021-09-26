import re
import spacy

from base.builder import Builder

'''
Targeted links: school-staff.html
https: //www.sydney.edu.au/engineering/about/contact-us.html
https: //www.sydney.edu.au/engineering/about.html
https://www.sydney.edu.au/research/centres.html
https: //www.sydney.edu.au/engineering/news-and-events/webinars-on-demand.html
https://www.sydney.edu.au/engineering/industry-and-community/external-advisory-bodies.html
https://www.sydney.edu.au/engineering/our-research/infrastructure-and-transport/centre-for-advanced-materials-technology.html
https: //www.sydney.edu.au/engineering/our-research/research-centres-and-institutes.html
https://www.sydney.edu.au/engineering/industry-and-community/partner-with-us.html
https://www.sydney.edu.au/engineering/industry-and-community/women-in-engineering.html
https://www.sydney.edu.au/engineering/industry-and-community/high-school-outreach.html
https://www.sydney.edu.au/engineering/industry-and-community/alumni.html
https://www.sydney.edu.au/engage/give.html
https://www.sydney.edu.au/scholarships/domestic/bachelors-honours/faculty/engineering.html#uniqueId_Q8W4Nf5q_7_button
Hot links: collaborate with us
Get contact info on the side
'''

def camel_case(st):
    output = ''.join(x for x in st.title() if x.isalnum())
    return output[0].lower() + output[1:]


class EngineeringBuilder(Builder):
    ''' JSON-LD KG Builder for Engineering entities '''

    def __init__(self, root_dir):
        '''Initialises the KG builder.
        '''
        self.name = 'engineering'
        self.category_lemma = {
            'Centres and institutes_': 'Centre',
            'Research_': 'Research',
            'Faculties and schools_': 'Department',
            'Study area_': 'IGNORE',
            'News_': 'News',
            'Event_': 'Event', 
            'Infrastructure_': 'Infrastructure',
            'Topic_': 'IGNORE',
            'People_': 'IGNORE',
            'Partnership_': 'CHECK',
            'Careers_': 'IGNORE',
            'Courses_': 'IGNORE',
            'University_': 'IGNORE',
            'Campus_': 'IGNORE',
        }
        self.school_lemma = {
            'aerospace': 'School of Aerospace, Mechanical and Mechatronic Engineering',
            'biomedical': 'School of Biomedical Engineering',
            'chemical': 'School of Chemical and Biomolecular Engineering',
            'civil': 'School of Civil Engineering',
            'computer': 'School of Computer Science',
            'electrical': 'School of Electrical and Information Engineering',
            'project': 'School of Project Management'
        }
        self.ignore_titles = ['about', 'research centres and institutes', 'contact us', 'schools', 'who was sir william tyree?', 'how to engage']
        super().__init__(root_dir)

    def _parse(self):

        nlp = spacy.load("en_core_web_sm")
        
        # For each page
        for url, page in self.data.items():
            
            url_directory = url.split('/')[4]
            url_file = (url.split('/')[-1]).replace('.html','')
            category = ''
            
            # Categorise the page
            if 'category' in page:
                category = self.category_lemma[page['category']['text']]

            if 'category' not in page or category == 'CHECK': 
                if '/news-and-events/' in url:
                    category = 'News'
                elif 'do-not-publish' in url:
                    category = 'IGNORE'
                elif url_file == 'school-staff':
                    category = 'Staff'
                elif 'Centre' in page['title']['text'] and not 'Centred' in page['title']['text']:
                    category = 'Centre'
                elif 'Hub' in page['title']['text']:
                    category = 'Centre'
                elif '/laboratories-and-facilities/' in url:
                    category = 'Infrastructure'
                elif 'services' in page['title']['text'].lower():
                    category = 'Service'
                elif '/our-research/' in url:
                    category = 'Research'
                elif '/study/' in url:
                    category = 'IGNORE'
                elif '/about' in url:
                    category == 'IGNORE'
                else:
                    category == 'Research'
            
            for req in self.ignore_titles:
                if req in page['title']['text'].lower():
                    category = 'IGNORE'
            
            # If ignore
            if category == 'IGNORE':
                
                # Continue to next page
                continue

            # If news
            if category == 'News':
            
                # Continue for now
                continue

            # # If unknown
            # if category == 'UNKNOWN':
                
            #     # Continue for now
            #     continue
            
            # Create an entity
            entity = {}
            entity['@id'] = self._make_uri(url)
            entity['@type'] = 'Thing'
            entity['rdfs:label'] = page['title']['text']
            entity['homepage'] = url

            # Establish the description
            entity['description'] = ''
            if 'summary' in page:
                entity['description'] = page['summary']['text'] + '\n'
            if 'content' in page:
                for content in page['content']:
                    entity['description'] += content['text'] + '\n'

            # For each article
            if 'articles' in page:
                for article in page['articles']:
                    continue
                
                    # Establish relationship to article
                    # if 'href' in article:
                    #     if 'category' in article and article['category'] in categories:
                    #         prop = self.categories[article['category']['text']]
                    #     else:
                    #         prop = 'relatedTopic'
                    #     if prop not in entity:
                    #         entity[prop] = []
                    #     entity[prop].append({ '@id': self._make_uri(article['href']['text']) })

            # Establish contact info
            if 'contacts' in page:
                entity['phone'] = self._phone(page['contacts']['text'])
                entity['email'] = self._email(page['contacts']['text'])
                entity['address'] = self._address(page['contacts']['text'])
                entity['building'] = self._building(page['contacts']['text'])
                
            if 'location' in page: 
                entity['address'] = page['location']['text']
                entity['building'] = self._building(page['location']['text'])
            
            # Establish directors/heads
            entity['head'] = []
            entity['director'] = []
            if 'call_outs' in page:
                for call_out in page['call_outs']:
                    if 'href' in call_out and 'title' in call_out:
                        if 'director' in call_out['title']['text'].lower():
                            staff = self._expert([ call_out['href']['links'][0] ])
                            entity['director'].extend(staff) 
            
            # If  research
            if category == 'Research':
                
                # Establish type
                entity['@type'] = 'Research'

                # Establish experts
                if 'content' in page:
                    links = [ link for content in page['content'] for link in content['links']]
                    entity['expert'] = self._expert(links)

                # Establish facilities
                if 'content' in page:
                    links = [ link for content in page['content'] for link in content['links']]
                    entity['facility'] = self._facility(links)

                # Establish partners
                if 'description' in entity:
                    entity['partner'] = self._partner(entity['description'], nlp, url)

                # Establish sub disciplines
                entity['subDiscpline'] = []
                if 'accordions' in page:
                    for accordion in page['accordions']:

                        # If academic staff
                        if accordion['heading']['text'] == 'Academic staff':
                            entity['expert'] += self._expert(accordion['body']['links'])

                        # If research associate
                        elif accordion['heading']['text'] == 'Research associates':
                            entity['researchAssociate'] = self._expert(accordion['body']['links'])

                        # If honorary associate
                        elif accordion['heading']['text'] == 'Honorary associates':
                            entity['honoraryAssociate'] = self._person_from_name(accordion['body']['text'], nlp, url)
                            
                        else:
                            # Create project entity
                            project = {}
                            project['@id'] = self._make_uri(url + accordion['heading']['text'])
                            project['@type'] = 'Research'
                            project['rdfs:label'] = accordion['heading']['text']
                            project['homepage'] = url

                            # Establish the description
                            project['description'] = accordion['body']['text']

                            # Establish experts
                            project['expert'] = self._expert(accordion['body']['links'])

                            # Establish facilities
                            project['facility'] = self._facility(accordion['body']['links'])

                            # Establish partners
                            project['partner'] = self._partner(accordion['body']['text'], nlp, url)

                            # Add research to kg
                            self._add_entity(project)

                            entity['subDiscpline'].append({ '@id': project['@id'] })

            # If centre
            if category == 'Centre':

                # Establish type
                entity['@type'] = 'Centre'
                entity['centre'] = []
                entity['research'] = []
                entity['facility'] = []
                entity['service'] = []
                entity['expert'] = []
                entity['advisor'] = []
                entity['adminStaff'] = []

                # For each article
                if 'articles' in page:
                    for article in page['articles']:

                        if 'category' in article:

                            # Establish centres
                            if article['category']['text'] == 'Centres and institutes_':
                                entity['centre'].append({ '@id': self._make_uri(article['href']['links'][0]) })

                            # Establish services
                            elif 'services' in article['title']['text'] or 'consultancy' in article['title']['text']:
                                entity['service'].append({ '@id': self._make_uri(article['href']['links'][0]) })
                            
                            # Establish research
                            elif article['category']['text'] == 'Research_':
                                research = {}
                                research['@id'] = self._make_uri(article['href']['links'][0])
                                research['@type'] = 'Research'
                                research['homepage'] = article['href']['links'][0]
                                self._add_entity(research)
                                entity['research'].append({ '@id': self._make_uri(article['href']['links'][0]) })

                            # Establish facilities
                            elif article['category']['text'] == 'Infrastructure_':
                                entity['facility'].append({ '@id': self._make_uri(article['href']['links'][0]) })

                # For each accordion
                if 'accordions' in page:
                    for accordion in page['accordions']:

                        # Establish academics
                        is_academic = False
                        academic_words = {'academic', 'research', 'technical'}
                        for academic_word in academic_words:
                            if academic_word in accordion['heading']['text'].lower():
                                is_academic = True
                                break

                        # Establish advisors
                        is_advisory = False
                        advisory_words = {'advisory', 'board'}
                        for advisory_word in advisory_words:
                            if advisory_word in accordion['heading']['text'].lower():
                                is_advisory = True
                                break

                        # Establish admin staff
                        is_admin = False
                        admin_words = {'admin', 'staff'}
                        for admin_word in admin_words:
                            if admin_word in accordion['heading']['text'].lower():
                                is_admin = True
                                break
                        
                        if is_academic:
                            entity['expert'].append(self._expert(accordion['body']['links']))

                        elif is_academic:
                            entity['advisor'].append(self._expert(accordion['body']['links']))

                        elif is_academic:
                            entity['adminStaff'].append(self._expert(accordion['body']['links']))
                            
                        # Establish facilities
                        elif 'facilities' in accordion['heading']['text'].lower():
                            entity['facility'] = []
                            for link in accordion['body']['links']:
                                entity['facility'].append({ '@id': self._make_uri(link) })

                        # Establish services
                        elif 'services' in accordion['heading']['text'].lower():
                            entity['service'] = []
                            for link in accordion['body']['links']:
                                entity['service'].append({ '@id': self._make_uri(link) })
                
            # If infrastructure
            if category == 'Infrastructure':
                
                entity['@type'] = 'Facility'
                entity['facility'] = []

                # For each heading
                if 'content' in page:
                    for content in page['content']:
                        for heading in content['headings']:

                            # Create infrastructure entity
                            infrastructure = {}
                            infrastructure['@id'] = self._make_uri(url + heading)
                            infrastructure['@type'] = 'Facility'
                            infrastructure['homepage'] = url
                            infrastructure['rdfs:label'] = heading
                            
                            self._add_entity(infrastructure)
                            entity['facility'].append({ '@id': infrastructure['@id'] })
            
            # If school
            if category == 'Department':

                # Establish type
                entity['@id'] = self._make_uri(page['title']['text'])
                entity['@type'] = 'Department'
                entity['centre'] = []
                entity['research'] = []

                # For each accordion
                if 'accordions' in page:
                    
                    for accordion in page['accordions']:

                        # Ignore courses
                        is_course = False
                        course_words = {'scheme', 'degree', 'course', 'project', 'program', 'postgraduate'}
                        for course_word in course_words:
                            if course_word in accordion['heading']['text'].lower():
                                is_course = True
                                break
                        
                        if is_course:
                            continue

                        # Establish facilities
                        elif 'facilities' in accordion['heading']['text'].lower():
                            entity['facility'] = []
                            for link in accordion['body']['links']:
                                entity['facility'].append({ '@id': self._make_uri(link) })

                        # Establish services
                        elif 'services' in accordion['heading']['text'].lower():
                            entity['service'] = []
                            for link in accordion['body']['links']:
                                entity['service'].append({ '@id': self._make_uri(link) })

                        # Establish research
                        else:
                            for link in accordion['body']['links']:
                                if 'centre' in link or 'hub' in link:
                                    entity['centre'].append({ '@id': self._make_uri(link) })
                                else:
                                    entity['research'].append({ '@id': self._make_uri(link) })

                # For each article
                if 'articles' in page:
                    for article in page['articles']:

                        if 'category' in article:

                            # Establish centres
                            if article['category']['text'] == 'Centres and institutes_':
                                entity['centre'].append({ '@id': self._make_uri(article['href']['links'][0]) })

                            # Establish research
                            if article['category']['text'] == 'Research_':
                                entity['research'].append({ '@id': self._make_uri(article['href']['links'][0]) })

                if 'content' in page:
                    for content in page['content']:

                        # Establish centres
                        for link in content['links']:
                            link_suffix = link.split('/')[-1]
                            if 'centre' in link_suffix or 'hub' in link_suffix:
                                entity['centre'].append({ '@id': self._make_uri(link) })


            # If service
            if category == 'Service':

                entity['@type'] = 'Service'

                # For each accordion
                entity['specialty'] = []
                if 'accordions' in page:
                    for accordion in page['accordions']:

                        # Create service entity
                        service = {}
                        service['@id'] = self._make_uri(url + accordion['heading']['text'])
                        service['@type'] = 'Service'
                        service['rdfs:label'] = accordion['heading']['text']
                        service['homepage'] = url
                        service['description'] = accordion['body']['text']
                        service['contact'] = self._expert(accordion['body']['links'])

                        self._add_entity(service)
                        entity['specialty'].append({ '@id': service['@id'] })

            # If staff
            if category == 'Staff':
                
                # Get the school name
                school_name = ''
                for k in self.school_lemma:
                    if k in url:
                        school_name = self.school_lemma[k]
                
                # Establish type
                entity['@id'] = self._make_uri(school_name)
                entity['@type'] = 'Department'
                del entity['rdfs:label']
                del entity['description']
                entity['field'] = []
                
                # For each accordion
                for accordion in page['accordions']:

                    # Check if admin roles
                    admin_words = {'leadership', 'coordinator', 'admin', 'technical service', 'director'}
                    is_admin = False
                    for admin_word in admin_words:
                        if admin_word in accordion['heading']['text'].lower():
                            is_admin = True
                            break
                        
                    
                    # Establish admin role
                    if is_admin:
                        
                        # Map last names to ids
                        name_to_uri = {}
                        for link in accordion['body']['links']:
                            surname_matches = re.search('([^\.]*)(\.php|\.html)', link.replace('-', '.'))
                            if surname_matches:
                                surname = surname_matches.group(1).title()
                                name_to_uri[surname] = self._expert([link])
                            
                        # Map roles to staff
                        rows = accordion['body']['text'].split('.')
                        for row in rows:
                            row_split = row.split(',')
                            if len(row_split) == 2:
                                role = camel_case(row_split[1].strip())
                                surname = (row.split(',')[0]).split(' ')[-1]
                                if role not in entity:
                                    entity[role] = []
                                if surname in name_to_uri:
                                    entity[role].append(name_to_uri[surname][0])

                    # Establish field roles
                    else:
                        field = {}
                        field['@id'] = self._make_uri(accordion['heading']['text'])
                        field['@type'] = 'Field'
                        field['rdfs:label'] = accordion['heading']['text']
                        field['homepage'] = ''.join(url.split('/')[:-1])
                        field['expert'] = self._expert(accordion['body']['links'])
                        self._add_entity(field)
                        entity['field'].append(field)
                
            # Add entity to kg
            self._add_entity(entity) 


    def _address(self, text):
        match = re.search('Address[^\.]*', text)
        return match.group(0) if match else None
    
    def _building(self, text):
        match = re.search('J\d\d', text)
        return { '@id': self._make_uri(match.group(0)) } if match else None
    
    def _email(self, text):
        return re.findall('([a-zA-Z0-9+._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)', text)
    
    def _expert(self, links):
        experts =  []
        
        # For each link
        for link in links:

            slink = re.sub('\.html|\.php|\?.*', '', link)

            # Check if the link points to a person
            uid = None
            if '/engineering/people/' in slink:
                uid = slink.split('/people/')[1]
            elif '/about/our-people/academic-staff/' in slink:
                uid = slink.split('/academic-staff/')[1]
                if '-' in uid and '.' not in uid:
                    uid = re.sub('-', '.', uid)
            elif '/medicine/people/academics/profiles/' in slink:
                uid = slink.split('/profiles/')[1]

            # If link points to person
            if uid:
                if not 'engineering' in link:
                    person = {}
                    person['@id'] = self._make_uri(uid)
                    person['@type'] = 'AcademicStaff'
                    person['rdfs:label'] = uid.replace('.', ' ').title()
                    person['homepage'] = link
                    self._add_entity(person)
                
                experts.append({ '@id': self._make_uri(uid) })

        return experts

    def _facility(self, links):
        facilities = []

        # For each link
        for link in links:
            # If the link points to a facility
            if '/our-research/laboratories-and-facilities/' in link:
                s = link.split('/laboratories-and-facilities/')[1]

                # Create facility entity 
                s = re.sub('\.html|\?.*', '', s)
                name = s.replace('-', ' ').title()
                facility = {}
                facility['@id'] = self._make_uri(name)
                facility['@type'] = 'Facility'
                facility['rdfs:label'] = name
                facility['homepage'] = link
                self._add_entity(facility)
                facilities.append({ '@id': facility['@id'] })

        return facilities

    
    def _partner(self, text, nlp, link):
        partners = []
        
        # Find entity mentions in text
        matches = re.findall('Our partners:[^\.]*|Our collaborators[^\.]*|Industry partners:[^\.]*', text)
        match_str = '. '.join(matches)
        doc = nlp(match_str)
        
        # For each entity mentioned
        for ent in doc.ents:

            partner = {}
            partner['rdfs:label'] = ent.text

            # If person, create person entity
            if ent.label_ == 'PERSON':
                partner['@id'] = self._make_uri(ent.text)
                partner['@type'] = 'ExternalAssosciate'
                partner['homepage'] = link
                self._add_entity(partner)
                partners.append({ '@id': partner['@id'] })

            # If organisation, create organisation entity
            elif ent.label_ == 'ORG':
                partner['@id'] = self._make_uri(ent.text)
                partner['@type'] = 'ExternalOrganisation'
                partner['homepage'] = link
                self._add_entity(partner)
                partners.append({ '@id': partner['@id'] })
        
        return partners
    
    def _person_from_name(self, text, nlp, link):
        persons = []
        doc = nlp(text)

        # For each person mentioned
        for ent in doc.ents:
            if ent.label_ == 'PERSON':

                # Create person entity
                person = {}
                person['@id'] = self._make_uri(ent.text)
                person['@type'] = 'Person'
                person['rdfs:label'] = ent.text
                person['homepage'] = link
                self._add_entity(person)
                persons.append({ '@id': person['@id'] })

        return persons

    def _phone(self, text):
        phones = []
        phones.extend(re.findall('1800 [0-9]{3} [0-9]{3}', text))
        phones.extend(re.findall('\+61 [0-9] [0-9]{4} [0-9]{4}', text))
        return phones


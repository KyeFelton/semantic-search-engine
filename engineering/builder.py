import re
import spacy

from engineering.canonicaliser import *
from engineering.categoriser import *
from engineering.interpreter import *
from engineering.validator import *
from base.builder import Builder


def camel_case(st):
    output = ''.join(x for x in st.title() if x.isalnum())
    return output[0].lower() + output[1:]


class EngineeringBuilder(Builder):

    def __init__(self, root_dir):
        self.name = 'engineering'
        super().__init__(root_dir)

    def _parse(self):

        nlp = spacy.load("en_core_web_sm")

        # For each page
        for url, page in self.data.items():

            # Skip invalid pages
            if not validate_page(url, page):
                continue

            # Canonicalise url
            url, url_can = canonicalise(url)

            # Create an entity
            entity = {}
            entity['@id'] = self._make_uri(url)
            if 'category' not in page:
                page['category'] = ''
            entity['@type'] = categorise(url=url,
                                         title=page['title'],
                                         category=page['category'])
            if not url_can:
                entity['rdfs:label'] = page['title']
                entity['name'] = page['title']
                entity['homepage'] = url
            else:
                entity['rdfs:label'] = None
                entity['name'] = None
                entity['homepage'] = None
            if 'summary' in page:
                entity['summary'] = page['summary']
            elif 'body' in page['content'][0]:
                entity['summary'] = page['content'][0]['body']
            else:
                entity['summary'] = None
            entity['website'] = url
            entity['description'] = []

            custom_build = getattr(self, f'_build_{entity["@type"].lower()}', None)
            entity = custom_build(url=url, page=page, entity=entity, )

            # Establish contact info
            if 'contacts' in page:
                entity['phone'] = self._find_phone(page['contacts'])
                entity['email'] = self._find_email(page['contacts'])
                entity['address'] = self._find_address(page['contacts'])
                entity['building'] = self._find_building(page['contacts'])

            # Establish location
            if 'location' in page:
                entity['address'] = page['location']
                entity['building'] = self._find_building(page['location'])

            # Establish directors
            entity['director'] = []
            if 'call_outs' in page:
                for call_out in page['call_outs']:
                    if 'href' in call_out and 'title' in call_out:
                        if 'director' in call_out['title'].lower():
                            director = self._get_staff(call_out['href'])
                            entity['director'].append(director)

            # For each article
            if 'articles' in page:
                for article in page['articles']:

                    # Skip invalid articles
                    if not validate_article(article):
                        continue

                    # Canonicalise href
                    href, href_can = canonicalise(article['href'])
                    if href == url:
                        continue

                    # Create the entity

                    if 'category' not in article:
                        article['category'] = ''
                    typ = categorise(url=href,
                                     title=article['title'],
                                     category=article['category'])
                    ref = self._make_entity(uri=href,
                                            typ=typ,
                                            name=None,
                                            label=article['title'],
                                            homepage=href,
                                            summary=article['summary'])
                    self._add_entity(ref, False)

                    # Establish relationship
                    relation = ref['@type'].lower()
                    if relation not in entity:
                        entity[relation] = []
                    entity[relation].append({'@id': ref['@id']})

            self._add_entity(entity)

    def _build_alumnus(self, url, page, entity):
        entity['description'] = self._get_description(page=page,
                                                      content=True,
                                                      accordions=True)
        return entity

    def _build_centre(self, url, page, entity):
        entity['description'] = self._get_description(page=page,
                                                      content=True,
                                                      accordions=False)
        entity = self._map_relations(data=page['content'],
                                     entity=entity,
                                     source=url)
        entity['research'] = []
        entity['infrastructure'] = []

        # For each accordion
        if 'accordions' in page:
            for accordion in page['accordions']:

                # Identify context
                context = interpretate(accordion['heading'], 'research')

                if context == 'research':
                    research = self._make_entity(uri=url + accordion['heading'],
                                                 typ='Research',
                                                 name=accordion['heading'],
                                                 homepage=url,
                                                 summary=accordion['body'])
                    if 'links' in accordion:
                        research = self._map_relations(data=[accordion],
                                                       entity=research,
                                                       source=url)
                    self._add_entity(research)
                    entity['research'].append({'@id': research['@id']})

                elif context == 'infrastructure':
                    infrastructure = self._make_entity(uri=url + accordion['heading'],
                                                       typ='Infrastructure',
                                                       name=accordion['heading'],
                                                       homepage=url,
                                                       summary=accordion['body'])
                    self._add_entity(infrastructure)
                    entity['infrastructure'].append(infrastructure)

                else:
                    if 'links' in accordion:
                        if context not in entity:
                            entity[context] = []
                        pred_obj = self._map_links(links=accordion['links'],
                                                   source=url)
                        for pred, objs in pred_obj.items():
                            if pred in entity:
                                entity[pred].extend(objs)
                            else:
                                entity[pred] = objs

        return entity

    def _build_contact(self, url, page, entity):

        entity['@type'] = 'Department'
        entity['name'] = None
        entity['rdfs:label'] = None
        entity['homepage'] = url.replace('/school-staff', '')
        entity['website'] = url.replace('/school-staff', '')
        entity['@id'] = self._make_uri(entity['homepage'])


        # For each accordion
        if 'accordions' in page:
            for accordion in page['accordions']:

                # Identify context
                context = interpretate(accordion['heading'], 'field')

                # Create field of experts
                if context == 'field':
                    # field = self._make_entity(uri=entity['homepage'] + accordion['heading'],
                    #                           typ='Field',
                    #                           name=accordion['heading'],
                    #                           homepage=entity['homepage'],
                    #                           summary='')
                    entity = self._map_relations(data=[accordion],
                                                entity=entity,
                                                source=entity['homepage'])
                    # self._add_entity(field)
                    # entity['field'].append(field)

                # Create a staff role
                else:
                    rows = accordion['body'].split('.')
                    for row in rows:
                        row_split = row.split(',')
                        if len(row_split) == 2:
                            role = camel_case(row_split[1].strip())
                            if role not in entity:
                                entity[role] = []
                            for link in accordion['links']:
                                if link['text'] in row_split[0]:
                                    entity[role].append(self._get_staff(link['href']))

        return entity

    def _build_department(self, url, page, entity):
        entity['description'] = self._get_description(page=page,
                                                      content=True,
                                                      accordions=False)

        entity = self._map_relations(data=page['content'],
                                     entity=entity,
                                     source=url)

        if 'accordions' in page:
            entity = self._map_relations(data=page['accordions'],
                                         entity=entity,
                                         source=url)
        return entity

    def _build_event(self, url, page, entity):
        return entity

    def _build_generic(self, url, page, entity):
        entity['description'] = self._get_description(page=page,
                                                      content=True,
                                                      accordions=False)

        entity = self._map_relations(data=page['content'],
                                     entity=entity,
                                     source=url)

        if 'accordions' in page:
            entity = self._map_relations(data=page['accordions'],
                                         entity=entity,
                                         source=url)

        return entity

    def _build_infrastructure(self, url, page, entity):
        entity['infrastructure'] = []

        # For each heading
        for content in page['content']:
            if 'heading' in content and \
                    content['heading'] != 'Who was Sir William Tyree?.' and \
                    content['heading'] != 'Contact us':

                if content['heading'] == '$FIRST$' and 'body' in content:
                    entity['description'] = content['body']

                # Create infrastructure entity
                elif 'body' in content:
                    infrastructure = self._make_entity(uri=url + content['heading'],
                                                       typ='Infrastructure',
                                                       name=content['heading'].replace('.', ''),
                                                       homepage=url,
                                                       summary=content['body'])
                    infrastructure = self._map_relations(data=[content],
                                                         entity=infrastructure,
                                                         source=url)
                    self._add_entity(infrastructure)
                    entity['infrastructure'].append({'@id': infrastructure['@id']})

        return entity

    def _build_news(self, url, page, entity):
        entity['content'] = []
        entity['mention'] = []
        if 'date' in page:
            entity['datePublished'] = page['date']
        for content in page['content']:
            if 'heading' in content and content['heading'] != '$FIRST$':
                entity['content'].append(content['heading'])
            if 'body' in content:
                entity['content'].append(content['body'])
            if 'links' in content:
                pred_obj = self._map_links(links=content['links'],
                                           source=url)
                for objs in pred_obj.values():
                    entity['mention'].extend(objs)
        return entity

    def _build_research(self, url, page, entity):
        entity['description'] = self._get_description(page=page,
                                                      content=True,
                                                      accordions=False)

        entity['expert'] = []
        entity['partner'] = []
        entity['infrastructure'] = []
        entity['research'] = []

        entity = self._map_relations(data=page['content'],
                                     entity=entity,
                                     source=url)

        if 'accordions' in page:
            for accordion in page['accordions']:

                # Identify context
                context = interpretate(accordion['heading'], 'research')

                if context == 'research':
                    research = self._make_entity(uri=url + accordion['heading'],
                                                 typ='Research',
                                                 name=accordion['heading'],
                                                 homepage=url,
                                                 summary=accordion['body'])
                    research = self._map_relations(data=[accordion],
                                                   entity=research,
                                                   source=url)
                    self._add_entity(research)
                    entity['research'].append({'@id': research['@id']})

                else:
                    if 'links' in accordion:
                        if context not in entity:
                            entity[context] = []
                        pred_obj = self._map_links(links=accordion['links'],
                                                   source=url)
                        for pred, objs in pred_obj.items():
                            if pred in entity:
                                entity[pred].extend(objs)
                            else:
                                entity[pred] = objs
        return entity

    def _build_service(self, url, page, entity):
        entity['description'] = self._get_description(page=page,
                                                      content=True,
                                                      accordions=False)
        entity['service'] = []

        if 'accordions' in page:
            for accordion in page['accordions']:
                service = self._make_entity(uri=url + accordion['heading'],
                                            typ='Service',
                                            name=accordion['heading'],
                                            homepage=url,
                                            summary=accordion['body'])
                service = self._map_relations(data=[accordion],
                                              entity=service,
                                              source=url)
                self._add_entity(service)
                entity['service'].append({'@id': service['@id']})

        return entity

    def _find_address(self, text):
        match = re.search('Address[^\.]*', text)
        return match.group(0) if match else None

    def _find_building(self, text):
        match = re.search('J\d\d', text)
        if match:
            return {'@id': self._make_uri(match.group(0))}
        else:
            return None

    def _find_email(self, text):
        return re.findall('([a-zA-Z0-9+._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)', text)

    def _find_phone(self, text):
        phones = []
        phones.extend(re.findall('1800 [0-9]{3} [0-9]{3}', text))
        phones.extend(re.findall('\+61 [0-9] [0-9]{4} [0-9]{4}', text))
        return phones

    def _find_school(self, url):
        dictionary = {
            'aerospace': 'School of Aerospace, Mechanical and Mechatronic Engineering',
            'biomedical': 'School of Biomedical Engineering',
            'chemical': 'School of Chemical and Biomolecular Engineering',
            'civil': 'School of Civil Engineering',
            'computer': 'School of Computer Science',
            'electrical': 'School of Electrical and Information Engineering',
            'project': 'School of Project Management'
        }
        for k in dictionary:
            if k in url:
                return dictionary[k]
        return None

    def _get_description(self, page, content=False, accordions=False):
        description = []
        if content and 'content' in page:
            for section in page['content']:
                if 'body' in section:
                    description.append(section['body'])
        if accordions and 'accordions' in page:
            for accordion in page['accordions']:
                if 'body' in accordion:
                    description.append(accordion['body'])
        return description

    def _get_staff(self, url):
        staff = {}
        staff['@type'] = 'Staff'
        staff['homepage'] = url
        staff['website'] = url
        staff['name'] = None
        staff['summary'] = None

        uid = re.sub('\.html.*|\.php.*', '', url)
        if '/people/' in uid:
            if '/profiles/' in url:
                uid = uid.split('/profiles/')[1]
            else:
                uid = uid.split('/people/')[1]
        elif '/academic-staff/' in uid:
            uid = uid.split('/academic-staff/')[1]
            if '-' in uid and '.' not in uid:
                uid = re.sub('-', '.', uid)

        if '/phlookup.cgi?' in uid:
            name = (uid.split('&name=')[1]).split('&')[0]
            staff['@id'] = self._make_uri(name.replace('+', '.'))
            staff['rdfs:label'] = name.replace('+', ' ').title()
        else:
            staff['@id'] = self._make_uri(uid)
            staff['rdfs:label'] = ' '.join([i.title() for i in uid.split('.') if not i.isdigit()])

        self._add_entity(staff, False)
        return {'@id': staff['@id']}

    def _map_links(self, links, source):
        pred_obj = {}
        for link in links:

            # Skip invalid articles
            if 'href' not in link or 'text' not in link:
                continue
            elif not validate_url(link['href']):
                continue

            # Canonicalise href
            href, href_can = canonicalise(link['href'])
            if href == source:
                continue

            # Categorise the link
            obj = {}
            obj['@type'] = categorise(href, link['text'])

            # Create the entity
            if obj['@type'] == 'Staff':
                obj.update(self._get_staff(href))
            else:
                obj['@id'] = self._make_uri(href)
                obj['rdfs:label'] = link['text']
                obj['homepage'] = href
                obj['website'] = href
                obj['summary'] = None
                obj['name'] = None
                # TODO: Canonicalize entities with URIs based off URLs and entities with URIs based off names
                # if not href_can and \
                #         obj['@type'] == 'External' or \
                #         obj['@type'] == 'Centre':
                #     self._make_equivalent(obj, obj['name'])
                self._add_entity(obj)

            # Map pred to obj
            if obj['@type'] == 'Generic':
                pred = 'mention'
            elif obj['@type'] == 'External':
                pred = 'partner'
            elif obj['@type'] == 'Staff':
                pred = 'expert'
            else:
                pred = obj['@type'].lower()
            if pred not in pred_obj:
                pred_obj[pred] = []
            pred_obj[pred].append({'@id': obj['@id']})

        return pred_obj

    def _map_relations(self, data, entity, source):
        for section in data:
            if 'links' in section:

                pred_obj = self._map_links(section['links'], source)
                for pred, objs in pred_obj.items():
                    if pred in entity:
                        entity[pred].extend(objs)
                    else:
                        entity[pred] = objs
        return entity

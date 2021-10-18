import datetime
import json
import re
from titlecase import titlecase

from base.builder import Builder


class UnitBuilder(Builder):
    ''' JSON-LD KG Builder for Unit entities '''

    def __init__(self, root_dir):
        '''Initialises the KG construction.
        '''
        self.name = 'unit'
        with open(f'{root_dir}/synonyms.json') as f:
            self.synonyms = json.loads(f.read())
        super().__init__(root_dir)

    def _parse(self):
        '''Builds the KG.'''

        # For each unit
        for page in self.data:
            for url, unit in page.items():
                url = url.replace('.coredata.json', '.html')

                # Flatten dict structure
                unit.update(unit['attributes'])
                del unit['attributes']
                unit.update(unit['descriptiveDetails'][0])
                del unit['descriptiveDetails']
                unit.update(unit['eligibilities'])
                del unit['eligibilities']

                # Create unit entity
                homepage = url if str(datetime.datetime.now().year) in url else None
                entity = self._make_entity(uri=unit['id'],
                                           typ='Unit',
                                           name=unit['title'],
                                           label=unit['id'],
                                           homepage=homepage,
                                           website=url,
                                           summary=unit['description'])
                unit.update(entity)

                # Establish the department
                if 'department' in unit and unit['department']:
                    dept_name = unit['department']
                    dept_url = ''
                    for k, v in self.synonyms['department'].items():
                        if dept_name in v:
                            dept_url = k
                            break
                    if dept_url != '':
                        dept = self._make_entity(uri=dept_url,
                                                 typ='Department',
                                                 name=self.synonyms['department'][dept_url][0],
                                                 label=dept_name,
                                                 homepage=None,
                                                 summary=None)

                        self._add_entity(dept, False)
                        unit['department'] = {'@id': dept['@id']}
                    else:
                        del unit['department']

                # Establish the faculty
                if 'faculty' in unit and unit['faculty']:
                    fac_name = titlecase(unit['faculty'])
                    fac_url = ''
                    for k, v in self.synonyms['faculty'].items():
                        if fac_name in v:
                            fac_url = k
                            break
                    if fac_url != '':
                        faculty = self._make_entity(uri=fac_url,
                                                    typ='Faculty',
                                                    name=self.synonyms['faculty'][fac_url][0],
                                                    label=fac_name,
                                                    homepage=None,
                                                    summary=None)
                        self._add_entity(faculty, False)
                        unit['faculty'] = {'@id': faculty['@id']}
                    else:
                        del unit['faculty']

                # Establish the pre-requisites, co-requsities, prohibitions and assumed knowledge units
                for criterion in ['pre-requisites',
                                  'co-requisites',
                                  'prohibitions',
                                  'assumedKnowledge']:
                    if criterion in unit:
                        unit[criterion + 'Units'] = self._find_units(unit[criterion])

                # Establish the unit coordinator
                if 'staff' in unit:
                    coordinator = unit['staff']['coordinator']['details']
                    if coordinator is not None and 'Refer to the unit of study' not in coordinator:
                        unit['coordinator'] = coordinator
                del unit['staff']

                # TODO: Handle availabilities
                if 'availabilities' in unit:
                    del unit['availabilities']
                # # For each availability
                # if 'availabilities' in unit:
                #     for avail in unit['availabilities']:
                #
                #
                #
                #         # Establish the campus
                #         if 'locationCodeDesc' in avail:
                #             avail['location'] = {'@id': self._make_uri(avail['locationCodeDesc'])}
                #
                #         # Remove unwanted info
                #         unwanted = ['faculty',
                #                     'department',
                #                     'published',
                #                     'sessionName',
                #                     'locationCode',
                #                     'locationCodeDescr',
                #                     'deliveryModeDesc']
                #         for i in unwanted:
                #             if i in avail:
                #                 del [avail[i]]

                # Remove unwanted info
                unwanted = ['programOfStudy',
                            'aemCachedAt',
                            'startingYear',
                            'codeAlpha',
                            'codeNumeric',
                            'type']
                for i in unwanted:
                    if i in unit:
                        del [unit[i]]

                # Add unit to kg
                self._add_entity(unit)

    def _find_units(self, text):
        '''Returns the uris of all the units found within text.
        
        Args:
            text (str): The text containing unit codes.
            
        Returns
            (list): A list containing the uri of each unit found.'''
        if type(text) is not str:
            return []
        unit_codes = re.findall('\\b[A-Z]{4}[0-9]{4}', text)
        for code in unit_codes:
            entity = self._make_entity(uri=code,
                                       typ='Unit',
                                       name=None,
                                       label=code,
                                       homepage=None,
                                       summary=None)
            self._add_entity(entity, False)
        unit_urls = [{'@id': self._make_uri(code)} for code in unit_codes]
        return unit_urls if len(unit_urls) > 0 else []

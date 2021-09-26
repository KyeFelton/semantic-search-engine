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
        with open(f'{root_dir}/alt_names.json') as f:
            alt_names = json.loads(f.read())
        self.fac_map = {}
        for fac, names in alt_names['faculty'].items():
            for name in names:
                self.fac_map[name.lower()] = fac
        self.dep_map = {}
        for dep, names in alt_names['department'].items():
            for name in names:
                self.dep_map[name.lower()] = dep  
        super().__init__(root_dir)
    
    def _parse(self):
        '''Builds the KG.'''
        units = [ x['unit'] for x in self.data ]
        
        # For each unit
        for unit in units:
            
            # Flatten dict structure
            unit.update(unit['attributes'])
            del unit['attributes']
            unit.update(unit['descriptiveDetails'][0])
            del unit['descriptiveDetails']
            unit.update(unit['eligibilities'])
            del unit['eligibilities']
            
            # Create unit entity
            unit['@id'] = self._make_uri(unit['id'])
            unit['@type'] = 'Unit'
            unit['rdfs:label'] = unit['title']

            # Establish the department
            if 'department' in unit and unit['department']:
                department = {}
                department_name = unit['department']
                if department_name.lower() not in self.fac_map:
                    if department_name.lower() in self.dep_map:
                        department_name = self.dep_map[department_name.lower()]
                    else:
                        department_name = titlecase(department_name)
                    department['@id'] = self._make_uri(department_name)
                    department['@type'] = 'Department'
                    department['rdfs:label'] = department_name
                    self._add_entity(department, False)
                    unit['department'] = { '@id': department['@id'] }

            # Establish the faculty
            if 'faculty' in unit and unit['faculty']:
                faculty = {}
                faculty_name = unit['faculty']
                if faculty_name.lower() in self.fac_map:
                    faculty_name = self.fac_map[faculty_name.lower()]
                else:
                    faculty_name = titlecase(faculty_name)
                faculty['@id'] = self._make_uri(faculty_name)
                faculty['@type'] = 'Faculty'
                faculty['rdfs:label'] = faculty_name
                self._add_entity(faculty, False)
                unit['faculty'] = { '@id': faculty['@id'] }
            
            # Establish the pre-requisites, co-requsities, prohibitions and assumed knowledge units
            for criterion in ['pre-requisites', 'co-requisites', 'prohibitions', 'assumedKnowledge']:
                if criterion in unit:
                    unit[criterion + 'Units'] = self._find_units(unit[criterion])

            # Establish the unit coordinator
            if 'staff' in unit:
                coordinator = unit['staff']['coordinator']['details']
                if coordinator is not None and coordinator != 'Refer to the unit of study outline https://www.sydney.edu.au/units':
                    unit['coordinator'] = coordinator
            del unit['staff']

            # For each availability 
            if 'availabilities' in unit:
                for avail in unit['availabilities']:
                    
                    # Establish the campus
                    if 'locationCodeDesc' in avail:
                        avail['location'] = { '@id': self._make_uri(avail['locationCodeDesc']) }
                    
                    # Remove unwanted info
                    unwanted = ['faculty', 'department', 'published', 'sessionName', 'locationCode', 'locationCodeDescr', 'deliveryModeDesc']
                    for i in unwanted:
                            if i in avail:
                                del[avail[i]]
            
            # Remove unwanted info
            unwanted = ['programOfStudy', 'aemCachedAt', 'startingYear', 'codeAlpha', 'codeNumeric', 'type']
            for i in unwanted:
                    if i in unit:
                        del[unit[i]]

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
        unit_urls = [ { '@id': self._make_uri(code) } for code in unit_codes ]
        return unit_urls if len(unit_urls) > 0 else []
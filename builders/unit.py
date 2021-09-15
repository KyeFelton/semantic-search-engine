from builders.builder import Builder

import re

class UnitBuilder(Builder):

    def __init__(self, ifile):
        super().__init__(ifile)
    
    def build(self, data):
        units = [ x['unit'] for x in data ]
        
        # For each unit
        for unit in units:
            
            # Create a url
            unit['@id'] = self.make_url('unit', unit['id'])
            # Create a type
            unit['@type'] = 'Unit'
            
            # Flatten dict structure
            unit.update(unit['attributes'])
            del unit['attributes']
            unit.update(unit['descriptiveDetails'][0])
            del unit['descriptiveDetails']
            unit.update(unit['eligibilities'])
            del unit['eligibilities']
            
            # Establish faculty owner
            unit['faculty'] = { '@id': self.make_url('organisation', unit['faculty'].replace(' ', '_')) }
            # Establish department owner
            unit['department'] = { '@id': self.make_url('organisation', unit['department'].replace(' ', '_')) }
            # Establish the pre-requisites, co-requsities, prohibitions and assumed knowledge units
            for criterion in ['pre-requisites', 'co-requisites', 'prohibitions', 'assumedKnowledge']:
                if criterion in unit:
                    unit[criterion + 'Units'] = self.find_units(unit[criterion])

            # Extract unit coordinator name
            if 'staff' in unit:
                coordinator = unit['staff']['coordinator']['details']
                if coordinator is not None and coordinator != 'Refer to the unit of study outline https://www.sydney.edu.au/units':
                    unit['coordinator'] = coordinator
            # Remove empty staff items
            del unit['staff']

            # For each availability 
            if 'availabilities' in unit:
                for avail in unit['availabilities']:
                    # Establish the campus
                    if 'locationCodeDesc' in avail:
                        avail['location'] = { '@id': self.make_url('campus', avail['locationCodeDesc'].replace(' ', '_'))}
                    # Remove duplicate data
                    del avail['faculty']
                    del avail['department']
            
            # Remove course data - these semantics will be extracted from the course builder
            if 'programOfStudy' in unit:
                del unit['programOfStudy']

            # Remove metadata
            del unit['aemCachedAt']

            # Add unit to kg
            self.add_node(unit)


    # Find all the unit codes in a string and return their urls
    def find_units(self, text):
        if type(text) is not str:
            return None
        unit_codes = re.findall('\\b[A-Z]{4}[0-9]{4}', text)
        unit_urls = [ { '@id': self.make_url('unit', code) } for code in unit_codes ]
        return unit_urls if len(unit_urls) > 0 else None
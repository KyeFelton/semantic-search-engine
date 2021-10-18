from base.builder import Builder

class PlaceBuilder(Builder):
    ''' JSON-LD KG Builder for Place entities '''
    
    def __init__(self, root_dir):
        '''Initialises the KG builder.
        '''
        self.name = 'place'
        super().__init__(root_dir)

    def _parse(self):   
        '''Builds the KG.'''
        
        for k, v in self.data.items():

            url = k
            buildings = v[0]['buildings']
            amenities = v[1]['places']
            
            # For each building    
            for building in buildings:

                # Create building entity
                self._create_building(building, url)

            # For each amenity
            for amenity in amenities:
                
                # Create amenity entity
                self._create_amenity(amenity, url)

    def _create_amenity(self, amenity, url):
        '''Creates an amenity entity and adds it to the KG.'''

        # Create amenity entity
        amenity['@id'] = self._make_uri(f'amenity {amenity["id"]}')
        typ = amenity['type']['name']
        if 'bus service' in typ.lower():
            typ = 'bus service'
        # amenity['@type'] = self._create_class(typ, 'Amenity')
        amenity['@type'] = 'Amenity'
        amenity['rdfs:label'] = amenity['name']
        amenity['homepage'] = url
        amenity['website'] = url
        if 'description' in amenity:
            amenity['summary'] = amenity['description']
        elif 'campus' in amenity and 'name' in amenity['campus']:
            amenity['summary'] = f'Campus: {amenity["campus"]["name"]}'
        else:
            amenity['summary'] = ''

        if 'geocode' in amenity:
            amenity.update(amenity['geocode'])
            del amenity['geocode']

        # Establish the building location
        if 'building' in amenity:
            amenity['building'] = self._create_building(amenity['building'], url)

        # Establish the campus location
        if 'campus' in amenity:
            amenity['campus'] = self._create_campus(amenity['campus'], url)

        # TODO: Handle trading hours
        if 'tradinghours' in amenity:
            del amenity['tradinghours']

        # Remove unwanted data
        unwanted = ['type', 'links', 'staffonly']
        for i in unwanted:
                if i in amenity:
                    del[amenity[i]]
        
        # Add amenity to kg
        self._add_entity(amenity)

    def _create_building(self, building, url):
        '''Creates a building entity and adds it to the KG.'''
        
        # Create building entity
        if 'code' in building:
            building['@id'] = self._make_uri(building['code'])
        else:
            building['@id'] = self._make_uri(building['name'])
        building['@type'] = 'Building'
        building['rdfs:label'] = building['name']
        building['homepage'] = url
        building['website'] = url

        if 'geocode' in building:
            building.update(building['geocode'])
            del building['geocode']

        # Establish the campus location
        if 'campus' in building and 'name' in building['campus']:
            building['summary'] = f'Campus: {building["campus"]["name"]}'
            building['campus'] = self._create_campus(building['campus'], url)
        else:
            building['summary'] = ''

        # TODO: Handle trading hours
        if 'tradinghours' in building:
            del building['tradinghours']

        # Remove unwanted data
        unwanted = ['imageurl', 'staffonly', 'links']
        for i in unwanted:
                if i in building:
                    del[building[i]]
        
        # Add building to kg
        self._add_entity(building, False)

        return { '@id': building['@id'] }

    def _create_campus(self, campus, url):
        '''Creates a campus entity and adds it to the KG.'''
        
        # Create campus entity
        campus['@id'] = self._make_uri(campus['name'])
        campus['@type'] = 'Campus'
        campus['rdfs:label'] = campus['name']
        campus['homepage'] = url
        campus['website'] = url
        if 'summary' not in campus:
            campus['summary'] = 'Sydney University Campus'

        if 'geocode' in campus:
            campus.update(campus['geocode'])
            del campus['geocode']

        # Remove unwanted data
        unwanted = ['links']
        for i in unwanted:
                if i in campus:
                    del[campus[i]]

        # Add campus to kg
        self._add_entity(campus, False)

        return { '@id': campus['@id'] }
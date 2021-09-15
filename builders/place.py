from builders.builder import Builder

class PlaceBuilder(Builder):
    
    def __init__(self, ifile):
        super().__init__(ifile)
        self.context.update({
            'latitude': {
                '@type': 'xsd:double'
            },
                'longitude': {
                    '@type': 'xsd:double'
            }
        })


    def build(self, data):   

        # For each building    
        for building in data[0]['buildings']:
            # Add building to kg
            self.create_building(building)

        # For each amenity
        for amenity in data[1]['places']:
            # Add amenity to kg
            self.create_amenity(amenity)


    def create_campus(self, campus):
        
        # Create the url
        url = self.make_url('campus', campus['name'].replace(' ', '_'))

        # If campus is new, create the node
        if url not in self.urls:
            campus['@id'] = url
            campus['@type'] = 'Campus'

            # Add to seen urls
            self.urls.add(url)
            # Add campus to kg
            self.add_node(campus)

        return { '@id': url }


    def create_building(self, building):
        
        # Create the url
        if 'code' in building:
            url = self.make_url('building', building['code'])
        else:
            url = self.make_url('building', building['name'])

        # If building is new, create the node
        if url not in self.urls:
            building['@id'] = url
            building['@type'] = 'Building'

            # Establish the campus location
            if 'campus' in building:
                building['campus'] = self.create_campus(building['campus'])
            
            # Add to seen urls
            self.urls.add(url)
            # Add building to kg
            self.add_node(building)

        return { '@id': url }

    def create_amenity(self, amenity):

        # Create the url
        amenity['@id'] = self.make_url('amenity', amenity['id'])
        # Create the type
        amenity['@type'] = self.create_class(amenity['type']['name'], 'Amenity')

        # Establish the building location
        if 'building' in amenity:
            amenity['building'] = self.create_building(amenity['building'])

        # Establish the campus location
        if 'campus' in amenity:
            amenity['campus'] = self.create_campus(amenity['campus'])
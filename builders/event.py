import datetime

from builders.builder import Builder

event_type = {
    1: 'Seminar',
    2: 'Conference',
    3: 'Exhibition',
    4: 'Performance',
    5: 'Fair',
    6: 'Celebration',
    7: 'RecreationEvent',
    8: 'CommunityEvent'
}

area_of_interest = {
    1: 'Science',
    2: 'Business',
    3: 'Environment',
    4: 'Health',
    5: 'Art',
    6: 'Diversity',
    7: 'Law',
    8: 'Government',
    9: 'Politics',
    10: 'General'
}

class EventBuilder(Builder):

    def __init__(self, ifile):
        super().__init__(ifile)
        self.context.update({    
            'start_datetime': {
                '@type': 'xsd:dateTime'
            },
            'end_datetime': {
                '@type': 'xsd:dateTime'
            },
            'multipleDates': {
                '@type': 'xsd:dateTime'
            },
            'cost': {
                '@type': 'xsd:integer'
            },
            'register_here': {
                '@type': 'xsd:anyURI'
            }
        })

    def build(self, data):
        # For each event
        for event in data[0]['events']:

            # Create the url
            event['@id'] = self.make_url('event', str(event['id']))
            # Create the type
            event['@type'] = self.create_class(event_type[event['event_type']], 'Event')
            
            # Establish the areas of interest
            areas = []
            for i in event['area_of_interest']:
                areas.append(area_of_interest[i])
            event['area_of_interest'] = areas

            # Establish the dates
            dates = []
            for i in event['multipleDates']:
                date_str = datetime.datetime.strptime(i, "%d-%m-%Y").strftime("%Y-%m-%d") + 'T10:00:00+10:00'
                dates.append(date_str)
            event['multipleDates'] = dates

            # Add event to kg
            self.add_node(event, False)    

    
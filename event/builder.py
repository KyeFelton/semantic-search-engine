import datetime

from base.builder import Builder

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
    ''' JSON-LD KG Builder for Event entities '''

    def __init__(self, root_dir):
        '''Initialises the KG construction.

        Args:
            ifile (str): The filename containing the raw data. The file should be in JSON format.
        '''
        self.name = 'event'
        super().__init__(root_dir)

    def _parse(self):
        '''Builds the KG.'''

        # For each event
        for url, event in self.data.items():

            # Create event entity
            event['@id'] = self._make_uri(f'event {event["id"]}')
            event['@type'] = self._create_class(event_type[event['event_type']], 'Event')
            event['rdfs:label'] = event['title']
            event['homepage'] = url
            
            # Establish the areas of interest
            areas = []
            if 'area_of_interest' in event:
                for i in event['area_of_interest']:
                    areas.append(area_of_interest[i])
                event['area_of_interest'] = areas

            # Establish the dates
            dates = []
            if 'multipleDates' in event:
                for i in event['multipleDates']:
                    date_str = datetime.datetime.strptime(i, "%d-%m-%Y").strftime("%Y-%m-%d") + 'T10:00:00+10:00'
                    dates.append(date_str)
                event['multipleDates'] = dates

            # Establish time
            if 'timeTitle' in event:
                event['time'] = event['timeTitle']
                del event['timeTitle']

            # Establish registration
            if 'register_here' in event:
                event['registration'] = event['register_here']
                del event['register_here']
            
            # Remove unwanted data
            unwanted = ['publish', 'dateTitle', 'eventType', 'event_type', 'startDate', 'endDate', 'futureEvent', 'image', 'produced_by', 'imageSrc']
            for i in unwanted:
                if i in event:
                    del[event[i]]

            # Add event to kg
            self._add_entity(event, False)    

    
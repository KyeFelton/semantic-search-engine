import html
import re

from base.cleaner import Cleaner

class EventCleaner(Cleaner):

    def __init__(self, root_dir):
        self.name = 'event'
        super().__init__(root_dir)
    
    def _parse_value(self, v):
            return v
    
    def _sort(self):
        s = {}
        url = 'https://whatson.sydney.edu.au/event/'
        for event in self.data[0]['events']:
            s[f'{url}{event["id"]}'] = event
        
        self.data = s
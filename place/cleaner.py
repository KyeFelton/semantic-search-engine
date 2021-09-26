import html
import re

from base.cleaner import Cleaner

class PlaceCleaner(Cleaner):

    def __init__(self, root_dir):
        self.name = 'place'
        super().__init__(root_dir)
    
    def _parse_value(self, v):
            return v
    
    def _sort(self):
        self.data = { 'https://www.sydney.edu.au/maps/campuses/': self.data }
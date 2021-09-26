import html
import re

from base.cleaner import Cleaner

class UnitCleaner(Cleaner):

    def __init__(self, root_dir):
        self.name = 'unit'
        super().__init__(root_dir)
    
    def _parse(self):
            pass
    
    def _sort(self):
        pass
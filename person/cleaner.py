import html
import re

from base.cleaner import Cleaner

class PersonCleaner(Cleaner):

    def __init__(self, root_dir):
        self.name = 'person'
        self.url = 'https://www.sydney.edu.au/engineering/about/our-people/'
        super().__init__(root_dir)
    
    def _parse_value(self, v):
        '''Removes HTML syntax in text.
        '''
        if type(v) is str:
            # Transform end of paragraphs and headings to fullstop
            v = re.sub('<\/p>|<\/h.>', '. ', v)
            
            # Transform end of lists to commas
            v = re.sub('</li>', ', ', v)
            
            # Remove html syntax
            v = re.sub('\\t|\\r|\\u00a0', ' ', v)
            v = re.sub(
                '<[^>]*>|\\ufffd[^\\ufffd]*\\ufffd|&laquo;[^\\&raquo;]*\\&raquo;|&bull;', ' ', v)
            v = html.unescape(v)
            
            # Normalise punctuation and whitespace
            v = re.sub('\ {2,}', ' ', v)
            v = re.sub('[\ |,]{3,}', ', ', v)
            v = re.sub('[\ |.|,]{3,}', '. ', v)
            v = re.sub('[( .,)]*:[( .,)]*', ': ', v)
            v = re.sub('[( .,)]*;[( .,)]*', '; ', v)
            v = v.strip()
            
        return v
    
    def _sort(self):
        '''Merges items with equivalent ids.
        '''
        merged = {}
        for item in self.data:
            if 'id' not in item:
                raise KeyError('Data is missing \'id\' key')
            elif 'type' not in item:
                raise KeyError('Data is missing \'type\' key')
            url = f'{self.url}{item["type"]}/{item["id"]}.html' 
            if url in merged:
                merged[url].update(item)
            else:
                merged[url] = item
        self.data = merged

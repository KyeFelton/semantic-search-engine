import html
import json
import re
import validators

from base.cleaner import Cleaner


class EngineeringCleaner(Cleaner):

    def __init__(self, root_dir):
        self.name = 'engineering'
        self.redirects = {}
        with open(f'{root_dir}/redirects.json') as f:
            arr = json.loads(f.read())
        for i in arr:
            self.redirects.update(i)
        super().__init__(root_dir)
    
    def _parse_value(self, v):
        '''Removes HTML syntax in text, and retrieves the destination of redirected urls.
        '''
        if type(v) is str:

            # Retrieve destination of redirects
            if validators.url(v):
                if v in self.redirects:
                    return self.redirects[v]

            # Transform end of paragraphs and headings to fullstop
            v = re.sub('<\/p>|<\/h.>', '. ', v)

            # Transform end of lists to commas
            v = re.sub('</li>', ', ', v)

            # Remove html syntax
            v = re.sub('\\t|\\r|\\u00a0|\\n', ' ', v)
            v = re.sub(
                '<[^>]*>|\\ufffd[^\\ufffd]*\\ufffd|&laquo;[^\\&raquo;]*\\&raquo;|&bull;', ' ', v)
            v = html.unescape(v)

            # Normalise punctuation and whitespace
            v = re.sub('\ {2,}', ' ', v)
            v = re.sub('[\ |\,]{3,}', ', ', v)
            v = re.sub('[\ |\.|\,]{3,}', '. ', v)
            v = re.sub('[\ \.\,]*:[\.\,]+', ':', v)
            v = re.sub('[\ \.\,]*;[\.\,]+', ';', v)
            v = re.sub('[\ \.\,]*\?[\.\,]+', '?', v)

            return v.strip()

        else:
            return v
    
    def _sort(self):
        '''Merges items with equivalent ids.
        '''
        merged = {}
        for page in self.data:          
            
            if 'title' not in page or \
                ('summary' not in page and \
                'content' not in page and \
                'accordions' not in page and \
                'articles' not in page):
                continue
            
            url  = page['url'].replace(' ', '')
            del page['url']
            merged[url] = page
            
        self.data = merged
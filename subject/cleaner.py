import html
import re

from base.cleaner import Cleaner

class SubjectCleaner(Cleaner):

    def __init__(self, root_dir):
        self.name = 'subject'
        super().__init__(root_dir)
    
    def _parse_value(self, v):
        if type(v) is str:

            # Transform end of paragraphs and headings to fullstop
            v = re.sub('<\/p>|<\/h.>', '. ', v)

            # Transform end of lists to commas
            v = re.sub('</li>', ', ', v)

            # Remove html syntax
            v = re.sub('\\t|\\r|\\n|\\u00a0|\\n', ' ', v)
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
        merged = {}
        for page in self.data:
            for k, v in page.items():
                if 'coredata.json' in k:
                    url = k.replace('.coredata.json', '.html')
                else:
                    url = k.replace('.explorer.json', '.html')
                if url not in merged:
                    merged[url] = {}
                merged[url].update(v)
        self.data = merged

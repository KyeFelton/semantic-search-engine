import html
import re

from base.cleaner import Cleaner

class EngineeringCleaner(Cleaner):

    def __init__(self, root_dir):
        self.name = 'engineering'
        super().__init__(root_dir)
    
    def _parse_value(self, v):
        '''Removes HTML syntax in text.
        '''
        if type(v) is str:

            check = False
            if 'b-contact-information' in v:
                check = True

            # Get links
            links = re.findall('\/\/[\w_-]+(?:(?:\.[\w_-]+)+)[\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-]?', v)
            links = [ f'https:{link}' for link in links ]

            # Get headings
            heading_matches = re.findall('<h.>(.*?)<\/h.>', v)
            headings = []
            for match in heading_matches:
                headings.append(re.sub('<[^>]*>', '', match))

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
            v = re.sub('[\ |,]{3,}', ', ', v)
            v = re.sub('[\ |.|,]{3,}', '. ', v)
            v = re.sub('[( .,)]*:[( .,)]*', ': ', v)
            v = re.sub('[( .,)]*;[( .,)]*', '; ', v)
            v.strip()

            return { 'text': v, 'headings': headings, 'links': links }
        
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
            
            url  = page['url']['text'].replace(' ', '')
            del page['url']
            merged[url] = page
            
            text = ''
            text += url + '\n'
            if 'title' in page: 
                text += page['title']['text'] + '\n'
            if 'subtitle' in page: 
                text += page['subtitle']['text'] + '\n'
            if 'summary' in page: 
                text += page['summary']['text'] + '\n' 
            text += '\n'
            if 'content' in page:
                for content in page['content']:
                    text += content['text'] + '\n'
                text += '\n'
            if 'accordion' in page:
                for accordion in page['accordion']:
                    text += accordion['heading']['text'] + '\n'
                    text += accordion['body']['text'] + '\n'
                text += '\n'
            if 'articles' in page:
                for article in page['articles']:
                    if 'title' in article:
                        text += article['title']['text'] + '\n'
                    if 'summary' in article:
                        text += article['summary']['text'] + '\n'
                text += '\n'
            if 'call_outs' in page:
                for call_out in page['call_outs']:
                    if 'title' in call_out:
                        text += call_out['title']['text'] + '\n'
                    if 'quote' in call_out:
                        text += call_out['quote']['text'] + '\n'
                    if 'text' in call_out:
                        text += call_out['text']['text'] + '\n'
                text += '\n'
            self.pages.append({ page['title']['text']: text })
            
        self.data = merged
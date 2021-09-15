import html
import json
import re


class Cleaner:


    def __init__(self, filename=None):
        if filename:
            with open(filename) as f:
                self.data = json.loads(f.read())
        else:
            self.data = None


    def load(self, filename):
        with open(filename) as f:
            self.data = json.loads(f.read())
    

    def merge(self):
        if self.data is None:
            raise AttributeError('No data has been loaded.')
        merged = {}
        for item in self.data:
            if item['id'] in merged:
                merged[item['id']].update(item)
            else:
                merged[item['id']] = item
        self.data = merged
    

    def clean(self, data=None):
        if self.data is None:
            raise AttributeError('No data has been loaded.')
        elif data is None:
            return clean(self.data)
        else:
            if type(data) is dict:
                for k, v in data.items():
                    data[k] = clean(v)
            elif type(data) is list:
                for i in range(0, len(data)):
                    data[i] = clean(data[i])
            elif type(data) is str:
                data = remove_html(data)
            return data

    
    def save(self, filename):
        with open(filename, 'w') as f:
            try:
                f.write(json.dumps(list(data.values())))
            except AttributeError as e:
                f.write(json.dumps(list(data)))


    def replace_pattern(self, old_pattern, new_pattern, text):
        modifier = re.compile(old_pattern)
        return re.sub(modifier, new_pattern, text)


    def remove_html(self, text):
        text = replace_pattern('<\/p>|<\/h.>', '. ', text) # transform end of paragraphs and headings to fullstop
        text = replace_pattern('</li>', ', ', text) # transform end of lists to commas
        text = replace_pattern('\\u00a0|\\n|\\t|<[^>]*>|\\ufffd[^\\ufffd]*\\ufffd|&laquo;[^\\&raquo;]*\\&raquo;', ' ', text) # remove html tags
        text = html.unescape(text) # remove special html characters
        text = replace_pattern('\ {2,}', ' ', text) # remove 2+ spaces
        text = replace_pattern('[\ |,]{3,}', ', ', text) # correct inconsistent comma placement
        text = replace_pattern('[\ |.|,]{3,}', '. ', text) # correct inconsistent fullstop placement
        text = replace_pattern('[( .,)]*:[( .,)]*', ': ', text) # correct inconsistent colon placement
        text = replace_pattern('[( .,)]*;[( .,)]*', '; ', text) # correct inconsistent semicolon placement
        text = text.strip()
        return text

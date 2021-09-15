import html
import json
import os
import re        
    

def clean(ifile, ofile, merge=False):
    with open(ifile) as f:
            data = json.loads(f.read())

    if merge: 
        data = merge_data(data)
    data = clean_recursive(data)
    
    if os.path.exists(ofile):
        os.remove(ofile)
    with open(ofile, 'w') as f:
        try:
            f.write(json.dumps(list(data.values())))
        except AttributeError as e:
            f.write(json.dumps(list(data)))


def merge_data(data):
    if data is None:
        raise ValueError('Data cannot be of type None.')
    merged = {}
    for item in data:
        if 'id' not in item:
            raise KeyError('Data is missing \'id\' key')
        elif item['id'] in merged:
            merged[item['id']].update(item)
        else:
            merged[item['id']] = item
    return merged
    

def clean_recursive(data):
    if type(data) is dict:
        for k, v in data.items():
            data[k] = clean_recursive(v)
    elif type(data) is list:
        for i in range(0, len(data)):
            data[i] = clean_recursive(data[i])
    elif type(data) is str:
        data = remove_html(data)
    return data


def replace_pattern(old_pattern, new_pattern, text):
    modifier = re.compile(old_pattern)
    return re.sub(modifier, new_pattern, text)


def remove_html(text):
    text = replace_pattern('<\/p>|<\/h.>', '. ', text) # transform end of paragraphs and headings to fullstop
    text = replace_pattern('</li>', ', ', text) # transform end of lists to commas
    text = replace_pattern('\\u00a0|\\n|\\t|\\r|<[^>]*>|\\ufffd[^\\ufffd]*\\ufffd|&laquo;[^\\&raquo;]*\\&raquo;', ' ', text) # remove html tags
    text = html.unescape(text) # remove special html characters
    text = replace_pattern('\ {2,}', ' ', text) # remove 2+ spaces
    text = replace_pattern('[\ |,]{3,}', ', ', text) # correct inconsistent comma placement
    text = replace_pattern('[\ |.|,]{3,}', '. ', text) # correct inconsistent fullstop placement
    text = replace_pattern('[( .,)]*:[( .,)]*', ': ', text) # correct inconsistent colon placement
    text = replace_pattern('[( .,)]*;[( .,)]*', '; ', text) # correct inconsistent semicolon placement
    text = text.strip()
    return text

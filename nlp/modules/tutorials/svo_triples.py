import json

url = "https://www.sydney.edu.au/engineering/news-and-events/2019/03/29/new-funding-laying-foundation-for-hydrogen-resistant-steels.html"

with open('./data/cleaned/page.json') as f:
    data = json.loads(f.read())

text = ''
for e in data:
    if e['url'].replace(' ','') == url:
        for content in e['content']:
            text += content

article = text

import pandas as pd
import numpy as np
import textacy

#top keyterms from each keyword extraction algorithm
keyterms = ['hydrogen embrittlement','Proessor Cairney','Dr Yi-Sheng','ARC Linkage Project grant', 'hydrogen-resistant steel']

#create doc object using SpaCy's en_core_web_sm model
doc = textacy.make_spacy_doc(article, lang='en_core_web_sm')

#extract relevant SVO patterns using Textacy
#doc is the same Doc object which was created earlier 
#line 11 returns a generator object, which contains 3-tuples (subject,verb,object)
SVOs = textacy.extract.subject_verb_object_triples(doc)
svos = []
for term in keyterms:
    for s in SVOs:
        dictionary = {'keyterm':None,'svo':None}
        print(s)
        svo_lemma = [t.lemma for t in s] #lemmatize svo patterns
        if term in svo_lemma:
            dictionary['keyterm'],dictionary['svo'] = term, s
            svos.append(dictionary)
        else:
            pass
svo_data = pd.DataFrame(svos)
# svo_data.to_csv('svo_data.csv')

#get relevent sentences
#doc.sents gives us a generator object that we can iterate over conatining sentences
#s.lemma_ returns the sentence with all tokens lemmatized
sentences = []
for term in keyterms:
    keyterm_sentences = [s for s in doc.sents if term in s.lemma_]
    for s in keyterm_sentences:
        dictionary = {'keyterm':None,'sentence':None}
        dictionary['keyterm'], dictionary['sentence'] = term, s
        sentences.append(dictionary)
sentence_data = pd.DataFrame(sentences)
# sentence_data.to_csv('sentence_data.csv')
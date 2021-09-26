import pandas as pd
import numpy as np
import textacy

def extract_svos(name, text, filepath, form='basic'):
    if form == 'basic':
        doc = textacy.make_spacy_doc(text, lang='en_core_web_sm')
        SVOs = textacy.extract.subject_verb_object_triples(doc)
        svo_data = pd.DataFrame(SVOs)
        svo_data.to_csv(filepath)

    elif form=='lemmatize':
        doc = textacy.make_spacy_doc(text, lang='en_core_web_sm')
        SVOs = textacy.extract.subject_verb_object_triples(doc)
        svos = []
        for s in SVOs:
            svo_lemma = [t.lemma_ for t in s] # unable to recognise t.lemma_
            svos.append(dictionary)
        svo_data = pd.DataFrame(svos)
        svo_data.to_csv(filepath)
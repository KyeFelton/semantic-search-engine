import csv
import pandas as pd
import numpy as np
import spacy
import textacy

def extract_entities(name, text, filepath, form='spacy'):
    if form == 'basic':
        doc = textacy.make_spacy_doc(text, lang='en_core_web_sm')
        entities = textacy.extract.entities(doc)
        entity_data = pd.DataFrame(entities)
        entity_data.to_csv(filepath)

    if form == 'spacy':
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(text)

        with open(filepath, mode='w') as f:
            writer = csv.writer(f, delimiter=',')
            for ent in doc.ents:
                row = [ent.text, ent.label_]
                writer.writerow(row)
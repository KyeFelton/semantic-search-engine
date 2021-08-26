import spacy
import json
# import requests
# from spacy import displacy
# import en_core_web_sm

nlp = spacy.load('en_core_web_sm')

# from spacy.tokens import Span
# from spacy.matcher import Matcher

# import matplotlib.pyplot as plot
from tqdm import tqdm
# import networkx as ntx

# %matplotlib inline # <-- required for jupiter notebook


# https://neptune.ai/blog/web-scraping-and-knowledge-graphs-machine-learning
def extract_entities(sents):
    # chunk one
    enti_one = ""
    enti_two = ""

    dep_prev_token = ""  # dependency tag of previous token in sentence

    txt_prev_token = ""  # previous token in sentence

    prefix = ""
    modifier = ""

    for tokn in nlp(sents):
          # chunk two
          # move to next token if token is punctuation

        if tokn.dep_ != "punct":
            #  check if token is compound word or not
            if tokn.dep_ == "compound":
                prefix = tokn.text
                # add the current word to it if the previous word is 'compound’
                if dep_prev_token == "compound":
                    prefix = txt_prev_token + " " + tokn.text

            # verify if token is modifier or not
            if tokn.dep_.endswith("mod") == True:
                modifier = tokn.text
                # add it to the current word if the previous word is 'compound'
                if dep_prev_token == "compound":
                    modifier = txt_prev_token + " " + tokn.text

            # chunk3
            if tokn.dep_.find("subj") == True:
                enti_one = modifier + " " + prefix + " " + tokn.text
                prefix = ""
                modifier = ""
                dep_prev_token = ""
                txt_prev_token = ""

            # chunk4
            if tokn.dep_.find("obj") == True:
                enti_two = modifier + " " + prefix + " " + tokn.text

            # chunk 5
            # update variable
            dep_prev_token = tokn.dep_
            txt_prev_token = tokn.text

    return [enti_one.strip(), enti_two.strip()]


def extract_sentences(page):
    text = ''

    if page['summary']:
        text += page['summary'] + ' '
    if page['content']:  
        for section in page['content']:
            text += section + ' '
    if page['accordions']:
        for accordion in page['accordions']:
            text += accordion['body'] + ' '
    return text

if __name__ == '__main__':

    with open('../scraped_data/page.json') as f:
        data = json.loads(f.read())

    text = ''

    for page in data[:20]:
        text += extract_sentences(page)

    doc = nlp(text)

    pairs_of_entities = []
    for i in tqdm(doc.sents): 
        pairs_of_entities.append(extract_entities(str(i)))

    print(pairs_of_entities)






        
    # text = []

    # if page['summary']:
    #     text.append(page['summary'])
    # if page['content']:  
    #     for section in page['content']:
    #         text.append(section)


    # if isinstance(type(page['summary']), str):
    #     text += page['summary'] + ' '
    # if isinstance(type(page['content']), str):
    #     text += page['content'] + ' ' 
    # elif isinstance(type(page['content']), list):
    #     for section in page['content']:
    #         text += section + ' '
    # if isinstance(type(page['accordions']), list):
    #     for accordion in page['accordions']:
    #         if isinstance(type(accordion['body']), str):
    #             text += accordion['body'] + ' '
    #         elif isinstance(type(accordion['body']), list):
    #             for section in accodion['body']:
    #                 text += section + ' '


    # doc = nlp(text)
    # return str(doc.sents)
    # print(text)


    # sentences = []
    # for section in text:
    #     doc = nlp(section)
    #     sentences.append(str(doc.sents))
    # print(sentences)
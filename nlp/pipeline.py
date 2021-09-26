import json
import os
import re

from modules.ner import *
from modules.keyterms import *
from modules.svo import *


def extract_semantics(typ, name, text):
    
    # Extract the keyterms
    file_png = './nlp/results/' + typ + '/' + name + '_keyterms.png'
    if os.path.exists(file_png): os.remove(file_png)
    file_csv = file_png[0:-3] + 'csv'
    if os.path.exists(file_csv): os.remove(file_csv)
    create_keyterm_graph(name, text, file_png, file_csv)

    # Extract the entities
    file_csv = './nlp/results/' + typ + '/' + name +'_entities.csv'
    if os.path.exists(file_csv): os.remove(file_csv)
    extract_entities(name, text, file_csv)

    # Extract the svos
    file_csv = './nlp/results/' + typ + '/' + name +'_svo.csv'
    if os.path.exists(file_csv): os.remove(file_csv)
    extract_svos(name, text, file_csv)


def people():
    # Load person data
    with open('./data/experiments/person.json') as f:
        persons = json.loads(f.read())

    # For each person
    for person in persons:

        # Get the text
        text = ''
        if person['blurb']: text += person['blurb'] + ' '
        if person['bio']: text += person['bio'] + ' '
        if person['currentProjects']: text += person['currentProjects'] + ' '
        
        # Extract the semantics
        extract_semantics('person', person['name'], text)

def centre():
    # Load centre data
    with open('./data/experiments/centre.json') as f:
        centres = json.loads(f.read())
    
    # For each centre
    for centre in centres:

        # Get the text
        text = ''
        if centre['summary']: text += centre['summary'] + ' '
        if centre['content']:
            for content in centre['content']:
                text += content + ' '
        if centre['accordions']:
            for accordion in centre['accordions']:
                text += accordion['body'] + ' '

        # Extract the semantics
        extract_semantics('centre', centre['title'], text)

def article():
    # Load article data
    with open('./data/experiments/article.json') as f:
        articles = json.loads(f.read())
    
    # For each article
    for article in articles:

        # Get the text
        text = ''
        if article['summary']: text += article['summary'] + ' '
        if article['content']:
            for content in article['content']:
                text += content + ' '

        # Extract the semantics
        extract_semantics('article', article['title'], text)

def expert():
    text = 'Our experts: Dr Shuaiwen Leon Song. Our partners: Professor Alvin Lebeck (Duke University, USA), Associate Professor Michael Taylor (University of Washington, USA), Dr Xin Fu (University of Houston, USA), Dr Lizy John (University of Texas at Austin, USA). Industry partners: Sara Hooker (Google Brain), Mike Zhan (Ambarella Inc), Yongchao Liu (Alibaba Research). AI-driven system design has become prevalent, from embedded systems such as IoT and edge computing to large-scale data centre and HPC system design. However, the current data-flow driven design has shown significant inefficiency on new deep learning networks. . By leveraging our unique research capability via looking into different design stacks from programming language, compiler and runtime to hardware customisation, we’re exploring other better alternatives (such as memory- and data-centric designs) to help practitioners build their software and hardware layers of the desired deep learning systems. . Our primary focus is to provide general strategies for designing accelerators or systems that can accommodate the unique aspects of emerging DL and ML networks. . We’re also exploring design principles and optimisation strategies for the emerging probabilistic machine learning models such as Bayesian Neural Networks and of Markov Chain Monte Carlo. . Our recent works have resulted in top HPC and architecture conferences including Supercomputing, ISCA and HPCA. .'
    text2 = 'Professor Alvin Lebeck'
    extract_semantics('expert', 'expert-trial', text2)

if __name__ == '__main__':
    
    text = 'Our experts: Dr Shuaiwen Leon Song. Our partners: Professor Alvin Lebeck (Duke University, USA), Associate Professor Michael Taylor (University of Washington, USA), Dr Xin Fu (University of Houston, USA), Dr Lizy John (University of Texas at Austin, USA). Industry partners: Sara Hooker (Google Brain), Mike Zhan (Ambarella Inc), Yongchao Liu (Alibaba Research). AI-driven system design has become prevalent, from embedded systems such as IoT and edge computing to large-scale data centre and HPC system design. However, the current data-flow driven design has shown significant inefficiency on new deep learning networks. . By leveraging our unique research capability via looking into different design stacks from programming language, compiler and runtime to hardware customisation, we’re exploring other better alternatives (such as memory- and data-centric designs) to help practitioners build their software and hardware layers of the desired deep learning systems. . Our primary focus is to provide general strategies for designing accelerators or systems that can accommodate the unique aspects of emerging DL and ML networks. . We’re also exploring design principles and optimisation strategies for the emerging probabilistic machine learning models such as Bayesian Neural Networks and of Markov Chain Monte Carlo. . Our recent works have resulted in top HPC and architecture conferences including Supercomputing, ISCA and HPCA. .'
    if 'Our partners:' in text:
        partner_str = ''
        match = re.search('Our partners:[^\.]*', text)
        partner_str += match.group(0)
        match = re.search('Industry partners:[^\.]*', text)
        if match: partner_str += match.group(0)
        match = re.search('Our collaborators[^\.]*', text)
        if match: partner_str += match.group(0)

        nlp = spacy.load("en_core_web_sm")
        doc = nlp(partner_str)

        partners = []
        for ent in doc.ents:
            if ent.label_ == 'ORG':
                partners.append(ent.text)

        print(partners)
    
    

        


    



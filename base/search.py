import argparse
import json
import numpy as np
import os
import pandas as pd
import stardog

from config import *

ap = argparse.ArgumentParser()

el_sparql_upload = '''select ?mention ?entity where {
                    graph <tag:stardog:api:docs:movies:article.txt> {
                        ?s rdfs:label ?mention ;
                        <http://purl.org/dc/terms/references> ?entity .
                    }
                }'''

el_sparql_direct = '''prefix docs: <tag:stardog:api:docs:>

select * {
  ?review :content ?text

  service docs:entityExtractor {
    []  docs:text ?text ;
        docs:mention ?mention ;
        docs:entity ?entity
  }
}

'''

def search(conn, query, limit):
    if type(limit) is int and limit > 0: query += ' limit ' + str(limit)
    output = conn.select(query)
    results = {} 
    for x in output['results'].values():
        for y in x:
            for k, v in y.items():
                if k not in results:
                    results[k] = []
                results[k].append(v['value'])
    return results

def keyterm_search(conn, terms, limit=0):
    query = f'select distinct ?uri ?score {{ ?uri ?p ?l. (?l ?score) <tag:stardog:api:property:textMatch> \'{terms}\' . }} order by desc(?score)' 
    results = search(conn, query, limit)
    if 'uri' in results and 'score' in results:
        return results['uri'], results['score'] 
    else:
        return [], []

def entity_search(conn, entity, limit=0):
    query = f'select distinct ?uri ?score {{ ?uri rdfs:label ?l. (?l ?score) <tag:stardog:api:property:textMatch> \'{entity}\' . }} order by desc(?score)'
    results = search(conn, query, limit)
    if 'uri' in results and 'score' in results:
        return results['uri'], results['score'] 
    else:
        return [], []

def label_search(conn, uri, limit=1):
    query = f'select ?label {{ <{uri}> rdfs:label ?label . }}'
    results = search(conn, query, limit)
    if 'label' in results:
        return results['label']
    else:
        return []

if __name__ == '__main__':

    ap.add_argument('query', metavar='Q', type=str, nargs='+', help='Query to be searched')
    ap.add_argument('-e', '--entities', required=False, help='Restrict search to only entity labels', action='store_true')

    query = ' '.join(vars(ap.parse_args())['query'])

    with stardog.Connection(db_name, **conn_details) as conn:
        if vars(ap.parse_args())['entities']:
            uris, scores  = entity_search(conn, query, 10)
        else:
            uris, scores  = keyterm_search(conn, query, 10)

    labels = [ label_search(conn, uri)[0] for uri in uris ]
    df = pd.DataFrame({ 'uris': uris, 'labels': labels, 'score': scores })
    print(df)

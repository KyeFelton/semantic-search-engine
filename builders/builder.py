from abc import ABC, abstractmethod
import hashlib
import inflect
import json
import os

ont_url = 'http://www.sydney.edu.au/ont/'
kg_url = 'http://www.sydney.edu.au/kg/'
inflect = inflect.engine()
valid_singular = ['Campus', 'Thesis']

class Builder():
    def __init__(self, ifile):
        self.urls = set()
        self.context = {
            'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
            'owl': 'http://www.w3.org/2002/07/owl#',
            'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
            '@vocab': ont_url,
            'stardog': 'tag:stardog:api:',
            'xsd': 'http://www.w3.org/2001/XMLSchema#'
        }
        
        self.kg = []
        with open(ifile) as f:
            data = json.loads(f.read())
        self.build(data)
        

    @abstractmethod
    def build(self, data):
        pass
    
    def get_id_from_str(self, string):
        m = hashlib.md5()
        m.update(string.encode('utf-8'))
        return m.hexdigest()[0:15]
    
    def validate_node(self, node):
        if '@id' not in node:
            raise KeyError(f'Missing @id key in node: {node}')
        elif type(node['@id']) is not str:
            raise ValueError(f'@id value is not str in node: {node}')
        elif '@type' not in node:
            raise KeyError(f'Missing @type key in node: {node}')
        elif type(node['@type']) is not str:
            raise ValueError(f'@type value is not str in node: {node}')
        else:
            pass

    # Its two hard to check which values are duplicates. 
    def add_node(self, node, duplicates=True):
        self.validate_node(node)

        # For now, just have to ignore duplicates.
        # if node['@id'] not in self.kg:
        #     self.kg[node['@id']] = node

        # For now, just permit duplicates
        self.kg.append(node)

        return node['@id']

    def standardise_name(self, original_name):
        if 'bus service' in original_name.lower():
            original_name = 'bus service'
        titled_name = original_name.replace('_', ' ').title()
        words = titled_name.split(' ')
        if words[-1] not in valid_singular:
            singular = inflect.singular_noun(words[-1])
            if singular:
                words[-1] = singular
        new_name = ''.join(words)
        return new_name

    def create_class(self, class_name, parent_class=None):
        clas = {}
        clas['@id'] = ont_url + self.standardise_name(class_name)
        clas['@type'] = 'owl:Class'
        if parent_class:
            clas['rdfs:subClassOf'] = { '@id': ont_url + parent_class }
        self.add_node(clas)
        return clas['@id']

    def create_property(self, prop_name, domain_classes, range_classes):
        prop = {}
        prop['@id'] = ont_url + prop_name
        prop['@type'] = 'owl:ObjectProperty'
        prop['rdfs:domain'] = [ { '@id': ont_url + clas } for clas in domain_classes ]
        prop['rdfs:range'] = [ { '@id': ont_url + clas } for clas in range_classes ]
        self.add_node(prop)


    def make_url(self, typ, identifier):
        return kg_url + typ + '-' + identifier



# if 'rdfs:domain' in node:
#     self.kg[node['@id']]['rdfs:domain'].extend(node['rdfs:domain'])
#     self.kg[node['@id']]['rdfs:range'].extend(node['rdfs:range'])
# elif 'rdfs:subClassOf' in node:
#     self.kg[node['@id']]['rdfs:subClassOf'].extend(node['rdfs:subClassOf'])
# else:


# if duplicates:
#     # Why isn't the duplicate being appended?
#     self.kg[node['@id']].append([ node ])
# else:
#     raise ValueError(f'node is already in graph: {node}')
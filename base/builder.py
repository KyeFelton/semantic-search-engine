from abc import abstractmethod
import hashlib
import inflect
import json
import os

ont_url = 'http://www.sydney.edu.au/kg/ont/'
kg_url = 'http://www.sydney.edu.au/kg/kg/'
inflect = inflect.engine()
valid_singular = ['Campus', 'Thesis']


class Builder:
    """ JSON-LD KG Builder
    """

    def __init__(self, root_dir):
        """Initialises the KG builder.
        """
        if not hasattr(self, 'name'):
            raise AttributeError('Builder requires a name.')
        self.root_dir = root_dir
        filename = f'{self.root_dir}/{self.name}/data/cleaned.json'
        with open(filename) as f:
            self.data = json.loads(f.read())

        self.uris = set()
        self.context = {
            'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
            'owl': 'http://www.w3.org/2002/07/owl#',
            'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
            '@vocab': ont_url,
            'stardog': 'tag:stardog:api:',
            'xsd': 'http://www.w3.org/2001/XMLSchema#',
            'latitude': {
                '@type': 'xsd:double'
            },
            'longitude': {
                '@type': 'xsd:double'
            }
        }
        self.kg = []
        self.pages = []

    def _add_entity(self, entity, duplicates=True):
        """Adds an entity to the KG.

        Args:
            entity (dict): The entity to be added, denoted in JSON-LD.
            duplicates (bool): Specifies whether duplicates are permitted or not.
        """
        if '@id' not in entity or 'https' in entity['@id']:
            raise ValueError(f'Missing @id in entity: {entity}')
        elif type(entity['@id']) is not str:
            raise ValueError(f'@id is not str in entity: {entity}')
        elif '@type' not in entity:
            raise ValueError(f'Missing @type in entity: {entity}')
        elif 'name' not in entity:
            raise ValueError(f'Missing name in entity: {entity}')
        elif 'rdfs:label' not in entity:
            raise ValueError(f'Missing rdfs:label in entity: {entity}')
        elif 'homepage' not in entity:
            raise ValueError(f'Missing homepage in entity: {entity}')
        elif 'website' not in entity:
            raise ValueError(f'Missing website in entity: {entity}')
        elif 'summary' not in entity:
            raise ValueError(f'Missing summary in entity: {entity}')
        else:
            if duplicates or entity['@id'] not in self.uris:
                self.kg.append(entity)
                self.uris.add(entity['@id'])
            return entity['@id']

    def build(self):
        """Initiates the building process.
        """
        self._parse()

        # Write data to .json file
        json_path = f'{self.root_dir}/{self.name}/data/kg.json'
        if os.path.exists(json_path):
            os.remove(json_path)
        with open(json_path, 'w') as f:
            f.write(json.dumps({
                '@context': self.context,
                '@graph': self.kg
            }))
        
    @abstractmethod
    def _parse(self):
        """Builds the KG.
        """
        pass
    
    def _create_class(self, name, parent=None):
        """Adds a class to the KG.

        Args:
            name (str): The name of the class.
            parent (str): The name of the parent class.
        """
        # Normalise name
        name = name.replace("'", '').replace('-',' ').replace('_', ' ')
        name = name.title()
        words = name.split(' ')
        if words[-1] not in valid_singular:
            singular = inflect.singular_noun(words[-1])
            if singular:
                words[-1] = singular
        name = ''.join(words)

        # Create class
        clas = {
            '@id': ont_url + name,
            '@type': 'owl:Class'
        }
        if parent:
            clas['rdfs:subClassOf'] = {'@id': ont_url + parent}

        # Add class to kg
        if clas['@id'] not in self.uris:
            self.kg.append(clas)
        return clas['@id']

    @staticmethod
    def _make_entity(uri, typ, name, homepage, summary, label=None, website=None, desc=None):

        def helper(a, b):
            if a:
                if b and type(b) is list:
                    b.append(a)
                elif b:
                    b = [a, b]
                else:
                    b = a
            return a, b

        name, label = helper(name, label)
        homepage, website = helper(homepage, website)
        summary, desc = helper(summary, desc)

        return {
            '@id': Builder._make_uri(uri),
            '@type': typ,
            'name': name,
            'rdfs:label': label,
            'homepage': homepage,
            'website': website,
            'summary': summary,
            'description': desc
        }

    def _make_equivalent(self, entity, new_uri):
        new = entity
        new['equivalent'] = {'@id': entity['@id']}
        new['@id'] = self._make_uri(new_uri)
        self._add_entity(new)

    @staticmethod
    def _make_uri(text):
        """Makes a uri for the given text.
        """
        m = hashlib.md5()
        m.update(text.lower().encode('utf-8'))
        return f'{kg_url}{m.hexdigest()[0:15]}'

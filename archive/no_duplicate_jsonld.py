from collections import abc

n1 = {
    'id': 'kye.felton',
    'books': [{
        'id': 1,
        'name': 'First book'
    }, {
        'id': 2,
        'name': 'Second book'
    }]
}

n2 = {
    'id': 'kye.felton',
    'books': [{
        'id': 3,
        'name': 'Third book'
    }, {
        'id': 1,
        'name': 'Best book'
    }]
}

n12 = {
    'id': 'kye.felton',
    'books': [{
        'id': 1,
        'name': [
            'First book',
            'Best book'
        ]
    }, {
        'id': 2,
        'name': 'Second book'
    }, {
        'id': 3,
        'name': 'Third book'
    }]
}

# str + str => list
# list + str => list
# list + list => list
# list + dict => list
# dict + dict => dict

def same_keys(d1, d2):
    return set(d1.keys()) == set(d2.keys())

def same_keys(d1, d2):
    return set(d1.keys()) == set(d2.keys())

def update_node(old, new):
    for k, v in new.items():
        if k in old:  
            if isinstance(v, abc.Mapping):
                if isinstance(old[k], abc.Mapping):
                    if same_keys(old[k], v):
                        return [ old[k], v ]
                    else:
                        update_node(old[k], v)
            if isinstance(v, abc.Sequence):
                if isinstance(old[k], abc.Sequence):
                    pass
            else:
                pass
        else:
            old[k] = v
    return n1



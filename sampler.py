import json

with open('./data/cleaned/person.json') as f:
    data = json.loads(f.read())

with open('./person.json', 'w') as f:
    f.write(json.dumps(data[0:10]))

# with open('./data/scraped/course.json') as f:
#     data = json.loads(f.read())

# with open('./course_sample.json', 'w') as f:
#     f.write(json.dumps(data[0:5]))

with open('./data/kg/person.json') as f:
    data = json.loads(f.read())

with open('./person_kg.json', 'w') as f:
    f.write(json.dumps(data['@graph'][0:10]))
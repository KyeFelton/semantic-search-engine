valid_domains = ['course', 'event', 'page', 'person', 'place', 'unit']
nlp_domains = ['page', 'person']

scraped_path = './data/scraped/'
cleaned_path = './data/cleaned/'
kg_path = './data/kg/'
sparql_tests_path = './testers/sparql/'

crawler_settings = {
    'LOG_ENABLED': False
}

conn_details = {
  'endpoint': 'http://localhost:5820',
  'username': 'admin',
  'password': 'admin'
}

db_name = 'usyd'
import json

if __name__ == '__main__':

    with open('../scraped_data/page.json') as f:
        data = json.loads(f.read())


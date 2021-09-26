import json
import scrapy

class PlaceSpider(scrapy.Spider):
    name = 'place'
    allowed_domains = ['www.sydney.edu.au']
    start_urls = ['https://www.sydney.edu.au/maps/campuses/']

    custom_settings = {
        'FEEDS': {
            'place.json': {'format': 'json'},
        }
    }

    def parse(self, response):
        url = 'https://www.sydney.edu.au/apps/maps/buildings.php?format=json'
        yield scrapy.Request(url, callback=self.parse_data, meta={'type': 'buildings'})
        
        url = 'https://www.sydney.edu.au/apps/maps/places.php?format=json'
        yield scrapy.Request(url, callback=self.parse_data, meta={'type': 'places'})

    def parse_data(self, response):
        data = {}
        if response.body:
            data[response.meta['type']] = json.loads(response.body)
        else:
            data[response.meta['type']] = None
        yield data
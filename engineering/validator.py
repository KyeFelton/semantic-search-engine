filter_urls = {
    'equals': [
        'https://www.sydney.edu.au/engineering/news-and-events/2017/06/20/making-life-easier-for-australian-farmers.html',
        'https://www.sydney.edu.au/engineering/schools.html',
        'https://www.sydney.edu.au/engineering/industry-and-community/consultancy-and-analytical-services.html',
        'https://www.sydney.edu.au/engineering/our-research/laboratories-and-facilities.html',
    ],
    'contains': [
        '/study/',
        '/units/',
        'www.sydney.edu.au/scholarships/',
        'javascript:void(0)',
        'mailto',
        '--test',
        'do-not-publish',
        'youtube',
        'drive.google.com',
        'hdl.handle.net',
        'forms.office.com',
        'uni-sydney.zoom.us'
    ]
}


def validate_url(url):
    if url in filter_urls['equals']:
        return False
    elif 'http' not in url:
        return False
    else:
        for u in filter_urls['contains']:
            if u in url:
                return False
    return True


def validate_article(article):
    if 'title' not in article:
        return False
    elif 'href' not in article:
        return False
    elif not validate_url(article['href']):
        return False
    else:
        return True


def validate_page(url, page):
    if not validate_url(url):
        return False
    elif 'title' not in page:
        return False
    elif len(page['content']) == 1 and \
            'body' not in page['content'][0] and \
            'accordions' not in page and \
            'articles' not in page:
        return False
    elif 'category' in page and 'topic' in page['category']:
        return False
    else:
        return True

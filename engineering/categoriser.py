defined = {
    'Generic': {
        'https://www.sydney.edu.au/engineering/our-research/research-centres-and-institutes.html',
    },
    'Department': {
        'https://www.sydney.edu.au/engineering/schools/school-of-aerospace-mechanical-and-mechatronic-engineering.html',
        'https://www.sydney.edu.au/engineering/schools/school-of-biomedical-engineering.html',
        'https://www.sydney.edu.au/engineering/schools/school-of-chemical-and-biomolecular-engineering.html',
        'https://www.sydney.edu.au/engineering/schools/school-of-civil-engineering.html',
        'https://www.sydney.edu.au/engineering/schools/school-of-computer-science.html',
        'https://www.sydney.edu.au/engineering/schools/school-of-electrical-and-information-engineering.html',
        'https://www.sydney.edu.au/engineering/schools/school-of-project-management.html',
    },
    'Alumnus': {
        'https://www.sydney.edu.au/engineering/our-research/infrastructure-and-transport/john-grill-institute-for-project-leadership/meet-john-grill-ao.html',
    },
    'Event': {
        'http://its.acfr.usyd.edu.au/blog/',
    }
}


def categorise(url='', title='', category='', default='Generic'):
    title = title.lower()
    category = category.lower()

    for k, v in defined.items():
        if url in v:
            return k

    types = ['Event', 'News', 'Contact', 'Course', 'Subject', 'Unit', 'Scholarship', 'Infrastructure', 'Centre', 'Publication', 'Social', 'External', 'Service', 'Staff', 'Research']
    for t in types:
        is_type = globals()[f'is_{t.lower()}'](url, title, category)
        if is_type:
            return t
    return default


def is_centre(url, title, category):
    if is_external(url, title, category):
        return False
    if 'centre ' in title or 'centre' == title[-6:]:
        return True
    elif 'center ' in title or 'center' == title[-6:]:
        return True
    elif 'hub ' in title or 'hub' == title[-3:]:
        return True
    elif 'institute ' in title or 'institute' == title[-9:]:
        return True
    elif 'centre' in category:
        return True
    else:
        return False


def is_contact(url, title, category):
    if 'school-staff' in url:
        return True
    # elif 'our people' in title:
    #     return True
    else:
        return False


def is_course(url, title, category):
    if '/courses/courses/' in url:
        return True
    else:
        return False


def is_event(url, title, category):
    if 'eventbrite.com' in url:
        return True
    elif 'e2ma.net' in url:
        return True
    elif 'event' in category:
        return True
    else:
        return False


def is_external(url, title, category):
    if 'sydney.edu.au' not in url:
        return True
    else:
        return False


def is_infrastructure(url, title, category):
    if '/laboratories-and-facilities/' in url:
        return True
    elif 'lab ' in title or 'lab' == title[-3:]:
        return True
    elif 'laboratory' in title or 'laboratories' in title:
        return True
    elif 'infrastructure' in category:
        return True
    else:
        return False


def is_news(url, title, category):
    if '/news-and-events/' in url:
        return True
    elif 'news' in category:
        return True
    else:
        return False


def is_publication(url, title, category):
    if 'library.usyd.edu.au' in url:
        return True
    elif 'doi.org' in url:
        return True
    elif 'onlinelibrary.wiley.com' in url:
        return True
    elif 'springer.com' in url:
        return True
    elif 'pubmed.ncbi.nlm.nih.gov' in url:
        return True
    elif 'ojs.aaai.org' in url:
        return True
    elif 'dl.acm.org' in url:
        return True
    elif 'journals.' in url:
        return True
    elif 'pubs.' in url:
        return True
    elif '/doi/' in url:
        return True
    elif '/publication/' in url:
        return True
    elif '/article/' in url:
        return True
    elif '/journals/' in url:
        return True
    elif '/proceedings/' in url:
        return True
    else:
        return False


def is_research(url, title, category):
    if '/our-research/' in url:
        return True
    elif 'research' in category:
        return True
    else:
        return False


def is_service(url, title, category):
    if 'services ' in title or 'services' == title[-8:]:
        return True
    elif 'consultanc' in title:
        return True
    elif 'service' in category:
        return True
    else:
        return False


def is_scholarship(url, title, category):
    if '/scholarships/' in url:
        return True
    else:
        return False


def is_social(url, title, category):
    if 'linkedin.com' in url:
        return True
    elif 'facebook.com' in url:
        return True
    elif 'instagram.com' in url:
        return True
    elif 'twitter.com' in url:
        return True
    else:
        return False


def is_subject(url, title, category):
    if '/courses/subject-areas/' in url:
        return True
    else:
        return False


def is_staff(url, title, category):
    if '/people/' in url or \
        '/academic-staff/' in url or \
            'phlookup.cgi?type=people' in url:
        return True
    else:
        return False


def is_unit(url, title, category):
    if '/courses/units-of-study/' in url:
        return True
    elif '/units/' in url:
        return True
    else:
        return False

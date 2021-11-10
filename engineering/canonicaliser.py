thesaurus = {
    'https://www.sydney.edu.au/engineering/our-research/infrastructure-and-transport/john-grill-institute-for-project-leadership.html': [
        'https://www.sydney.edu.au/engineering/our-research/infrastructure-and-transport/john-grill-institute-for-project-leadership/how-to-engage.html',
        'https://www.sydney.edu.au/engineering/our-research/infrastructure-and-transport/john-grill-institute-for-project-leadership/about-us.html',
        'https://www.sydney.edu.au/engineering/our-research/infrastructure-and-transport/john-grill-institute-for-project-leadership/cross-sectoral-expertise.html',
        'http://sydney.edu.au/john-grill-centre/',
        'https://www.youtube.com/watch?v=j3Siec1GsuQ',
    ],
    'https://www.sydney.edu.au/engineering/our-research/robotics-and-intelligent-systems/australian-centre-for-field-robotics.html': [
        'http://www.acfr.usyd.edu.au/',
    ],
    'https://www.sydney.edu.au/engineering/industry-and-community/consultancy-and-analytical-services/fluids-and-environmental-engineering-consultancy-services.html': [
        'https://www.sydney.edu.au/engineering/industry-and-government/consultancy-and-analytical-services/fluids-and-environmental-engineering-consultancy-services.html',
    ],
    'https://www.sydney.edu.au/engineering/our-research/food-products-process-and-supply-chain/centre-for-advanced-food-engineering.html': [
        'https://www.sydney.edu.au/engineering/our-research/food-products-process-and-supply-chain/centre-for-advanced-food-enginomics.html',
        'https://sydney.edu.au/engineering/our-research/food-products-process-and-supply-chain/centre-for-excellence-in-advanced-food-enginomics.html',
    ],
    'https://www.sydney.edu.au/engineering/our-research/food-products-process-and-supply-chain/arc-training-centre-for-the-australian-food-processing-industry.html': [
        'https://sydney.edu.au/engineering/our-research/food-products-process-and-supply-chain/arc-training-centre-for-the-australian-food-processing-industry.html',
        'https://www.sydney.edu.au/engineering/our-research/food-products-process-and-supply-chain/arc-training-centre-for-the-australian-food-processing-industry/our-people.html',
        'https://www.sydney.edu.au/engineering/our-research/food-products-process-and-supply-chain/arc-training-centre-for-the-australian-food-processing-industry/our-industry-partners.html',
    ],
    'https://www.sydney.edu.au/careers/home.html': [
        'https://www.sydney.edu.au/study/career-services.html',
    ],
    'https://www.sydney.edu.au/engineering/industry-and-community/the-warren-centre.html': [
        'http://www.thewarrencentre.org.au',
        'https://thewarrencentre.org.au/',
    ],
    'https://www.sydney.edu.au/charles-perkins-centre/home.html': [
        'https://www.sydney.edu.au/charles-perkins-centre/',
    ],
    'https://www.sydney.edu.au/engineering/our-research/robotics-and-intelligent-systems/australian-centre-for-field-robotics/mining.html': [
        'http://www.acfr.usyd.edu.au/rtcma/index.shtml',
    ],
}

def canonicalise(url):
    if 'sydney.edu.au' in url and 'www.sydney.edu.au' not in url:
        url = url.replace('sydney.edu.au', 'www.sydney.edu.au')
    if url not in thesaurus:
        for k, v in thesaurus.items():
            for i in range(0, len(v)):
                if url == v[i]:
                    return k, True
    return url, False
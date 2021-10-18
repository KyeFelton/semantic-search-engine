clues = {
    'expert': {
        'academic staff',
        'research team',
        'our researcher',
        'research staff',
        'academics',
    },
    'advisor': {
        'advisory',
        'advisor'
    },
    'associate': {
        'associate',
        'research fellow',
        'affiliate'
    },
    'partner': {
        'partner',
        'international universities'
    },
    'adminStaff': {
        'admin'
    },
    'technicalStaff': {
        'technical staff',
        'technical services'
    },
    'teachingStaff': {
        'learning facilitator',
        'teaching staff',
    },
    'manager': {
        'management',
        'leadership',
        'director',
        'coordinator',
    },
    'governance': {
        'governance',
        'committee',
    },
    'infrastructure': {
        'laboratory',
    },
    'service': {
        'services',
    },
    'event': {
        'seminar',
        'workshop',
    }
}

def interpretate(text='', default='related'):
    for k, v in clues.items():
        for term in v:
            if term in text.lower():
                return k
    return default

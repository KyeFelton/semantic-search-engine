import json
from titlecase import titlecase

from base.builder import Builder


class SubjectBuilder(Builder):
    ''' JSON-LD KG Builder for Subject entities '''

    def __init__(self, root_dir):
        '''Initialises the KG construction.
        '''
        self.name = 'subject'
        with open(f'{root_dir}/synonyms.json') as f:
            self.synonyms = json.loads(f.read())
        super().__init__(root_dir)

    def _parse(self):
        '''Builds the KG.'''

        # For each subject
        for url, subject in self.data.items():

            # Flatten dict structure
            if 'attributes' not in subject:
                continue
            subject.update(subject['attributes'])
            del subject['attributes']

            if 'par-zone4' in subject['content'] and \
                'subject-area-overview' in subject['content']['par-zone4'] and \
                'summary' in subject['content']['par-zone4']['subject-area-overview']:
                summary = subject['content']['par-zone4']['subject-area-overview']['summary']
                if 'About this' in summary:
                    summary = '.'.join(summary.split('About this')[1].split('.')[1:])
            else:
                summary = subject['description']

            # Create subject entity
            entity = self._make_entity(uri=subject['id'],
                                       typ='Subject',
                                       name=subject['title'],
                                       label=subject['id'],
                                       homepage=url,
                                       summary=summary)
            subject.update(entity)

            # Establish the faculty
            if 'facultyCode' in subject and subject['facultyCode']:
                fac_name = titlecase(subject['facultyCode'])
                fac_url = ''
                for k, v in self.synonyms['faculty'].items():
                    if fac_name in v:
                        fac_url = k
                        break
                if fac_url != '':
                    faculty = self._make_entity(uri=fac_url,
                                                typ='Faculty',
                                                name=self.synonyms['faculty'][fac_url][0],
                                                label=fac_name,
                                                homepage=None,
                                                summary=None)
                    self._add_entity(faculty, False)
                    subject['faculty'] = {'@id': faculty['@id']}
                else:
                    del subject['facultyCode']

            # Remove unwanted info
            unwanted = ['programOfStudy',
                        'collections',
                        'aemCachedAt',
                        'type',
                        'facultyCode',
                        'status',
                        'published',
                        'startingYear',
                        'url',
                        'template',
                        'path',
                        'lastModified',
                        'createdAt',
                        'content']
            for i in unwanted:
                if i in subject:
                    del [subject[i]]

            # Add subject to kg
            self._add_entity(subject)

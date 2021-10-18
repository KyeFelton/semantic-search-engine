import json
from titlecase import titlecase

from base.builder import Builder


class CourseBuilder(Builder):
    ''' JSON-LD KG Builder for Course entities '''

    def __init__(self, root_dir):
        '''Initialises the KG construction.
        '''
        self.name = 'course'
        with open(f'{root_dir}/synonyms.json') as f:
            self.synonyms = json.loads(f.read())
        super().__init__(root_dir)

    def _parse(self):
        '''Builds the KG.'''

        # For each course
        for url, course in self.data.items():

            # Flatten dict structure
            if 'attributes' not in course:
                continue
            course.update(course['attributes'])
            del course['attributes']
            if 'description' in course:
                summary = course['description']
            elif 'qualification' in course:
                summary = course['qualification']
            else:
                continue

            # Create course entity
            desc = course['content']['course-overview']['summary']
            if 'About this course.' in desc:
                desc = desc.split('About this course.')[1]
            entity = self._make_entity(uri=url,
                                       typ='Course',
                                       name=course['title'],
                                       label=course['id'],
                                       homepage=url,
                                       summary=summary,
                                       desc=desc)
            course.update(entity)

            # Establish subject areas
            course['subject'] = []
            if 'areasOfStudy' in course and 'subjectAreasByYear' in course['areasOfStudy']:
                for year in course['areasOfStudy']['subjectAreasByYear']:
                    for subject in year['pages']:
                        entity = self._make_entity(uri=subject['id'],
                                                   typ='Subject',
                                                   name=None,
                                                   label=subject['id'],
                                                   homepage=None,
                                                   summary=None)
                        self._add_entity(entity)
                        course['subject'].append({'@id': self._make_uri(subject['id'])})
                del course['areasOfStudy']

            # Establish units
            course['unit'] = []
            if 'collections' in course and 'unitsOfStudyByYear' in course['collections']:
                for year in course['collections']['unitsOfStudyByYear']:
                    for unit in year['pages']:
                        entity = self._make_entity(uri=unit['id'],
                                                   typ='Unit',
                                                   name=None,
                                                   label=unit['id'],
                                                   homepage=None,
                                                   summary=None)
                        self._add_entity(entity, False)
                        course['unit'].append({'@id': self._make_uri(unit['id'])})
                del course['collections']

            # Establish the department
            if 'department' in course and course['department']:
                dept_name = titlecase(course['department'])
                dept_url = ''
                for k, v in self.synonyms['department'].items():
                    if dept_name in v:
                        dept_url = k
                        break
                if dept_url != '':
                    dept = self._make_entity(uri=dept_url,
                                             typ='Department',
                                             name=self.synonyms['department'][dept_url][0],
                                             label=dept_name,
                                             homepage=None,
                                             summary=None)
                    self._add_entity(dept, False)
                    course['department'] = {'@id': dept['@id']}
                else:
                    del course['department']

            # Establish the faculty
            if 'faculty' in course and course['faculty']:
                fac_name = titlecase(course['faculty'])
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
                    course['faculty'] = {'@id': faculty['@id']}
                else:
                    del course['faculty']

            # TODO: Handle areas of study
            if 'areasOfStudy' in course:
                del course['areasOfStudy']

            # Remove unwanted info
            # TODO: Implement fee summaries and entry requirements
            unwanted = ['feeSummary',
                        'entryRequirements',
                        'aemCachedAt',
                        'active',
                        'coursePageSupportedYears',
                        'createdDate',
                        'departmentCode',
                        'group',
                        'published',
                        'startingYear',
                        'status',
                        'type',
                        'url',
                        'template',
                        'content']
            for i in unwanted:
                if i in course:
                    del [course[i]]

            # Add course to kg
            self._add_entity(course)

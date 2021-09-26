import json
from titlecase import titlecase

from base.builder import Builder

class CourseBuilder(Builder):
    ''' JSON-LD KG Builder for Course entities '''

    def __init__(self, root_dir):
        '''Initialises the KG construction.
        '''
        self.name = 'course'
        with open(f'{root_dir}/alt_names.json') as f:
            alt_names = json.loads(f.read())
        self.fac_map = {}
        for fac, names in alt_names['faculty'].items():
            for name in names:
                self.fac_map[name.lower()] = fac
        self.dep_map = {}
        for dep, names in alt_names['department'].items():
            for name in names:
                self.dep_map[name.lower()] = dep  
        super().__init__(root_dir)
    
    def _parse(self):
        '''Builds the KG.'''
        courses = [ x['course'] for x in self.data ]
        
        # For each course
        for course in courses:
            
            # Flatten dict structure
            course.update(course['attributes'])
            del course['attributes']
            
            # Create course entity
            course['@id'] = self._make_uri(course['id'])
            course['@type'] = self._create_class(course['qualification'], 'Course')
            course['rdfs:label'] = course['title']
            
            # Establish subject areas
            course['subjectAreas'] = []
            if 'subjectAreasByYear' in course['areasOfStudy']:
                for year in course['areasOfStudy']['subjectAreasByYear']:
                    for subject in year['pages']:
                        subject['@id'] = self._make_uri(subject['id'])
                        subject['@type'] = 'SubjectArea'
                        subject['rdfs:label'] = subject['title']
                        del subject['link']
                        del subject['type']
                        course['subjectAreas'].append({ '@id': subject['@id'] })
            del course['areasOfStudy']

            # Establish units
            course['units'] = []
            if 'unitsOfStudyByYear' in course['collections']:
                for year in course['collections']['unitsOfStudyByYear']:
                    for unit in year['pages']:
                        course['units'].append({ '@id': self._make_uri(unit['id'])})
                del course['collections']
            
            # Establish the department
            if 'department' in course and course['department']:
                department = {}
                department_name = course['department']
                if department_name not in self.fac_map:
                    if department_name.lower() in self.dep_map:
                        department_name = self.dep_map[department_name.lower()]
                    else:
                        department_name = titlecase(department_name)
                    department['@id'] = self._make_uri(department_name)
                    department['@type'] = 'Department'
                    department['rdfs:label'] = department_name
                    self._add_entity(department, False)
                    course['department'] = { '@id': department['@id'] }

            # Establish the faculty
            if 'faculty' in course and course['faculty']:
                faculty = {}
                faculty_name = course['faculty']
                if faculty_name.lower() in self.fac_map:
                    faculty_name = self.fac_map[faculty_name.lower()]
                else:
                    faculty_name = titlecase(faculty_name)
                faculty['@id'] = self._make_uri(faculty_name)
                faculty['@type'] = 'Faculty'
                faculty['rdfs:label'] = faculty_name
                self._add_entity(faculty, False)
                course['faculty'] = { '@id': faculty['@id'] }

            # Remove unwanted info
            # TODO: Implement fee summaries and entry requirements
            unwanted = ['feeSummary', 'entryRequirements', 'aemCachedAt', 'active', 'coursePageSupportedYears', 
                        'createdDate', 'departmentCode', 'group', 'published', 'startingYear', 'status', 'type']
            for i in unwanted:
                if i in course:
                    del[course[i]]

            # Add course to kg
            self._add_entity(course)
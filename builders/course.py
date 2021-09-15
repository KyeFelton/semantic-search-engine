from builders.builder import Builder

class CourseBuilder(Builder):

    def __init__(self, ifile):
        super().__init__(ifile)
    
    def build(self, data):
        courses = [ x['course'] for x in data ]
        
        # For each course
        for course in courses:
            
            # Create a url
            course['@id'] = self.make_url('course', course['id'])
            # Create a type
            course['@type'] = 'Course'

            # Flatten dict structure
            course.update(course['attributes'])
            del course['attributes']
            
            # Establish subject areas
            course['subjectAreas'] = []
            if 'subjectAreasByYear' in course['areasOfStudy']:
                for year in course['areasOfStudy']['subjectAreasByYear']:
                    for subject in year['pages']:
                        subject['@id'] = self.make_url('subject', subject['id'])
                        subject['@type'] = 'Subject'
                        course['subjectAreas'].append(subject)
            del course['areasOfStudy']

            # Establish units
            course['units'] = []
            if 'unitsOfStudyByYear' in course['collections']:
                for year in course['collections']['unitsOfStudyByYear']:
                    for unit in year['pages']:
                        course['units'].append({ '@id': self.make_url('unit', unit['id'])})
                del course['collections']
            
            # Establish department
            if 'department' in course and course['department']:
                course['department'] = { '@id': self.make_url('organisation', course['department'].title().replace(' ', '_')) }

            # Establish faculty
            if 'faculty' in course and course['faculty']:
                course['faculty'] = { '@id': self.make_url('organisation', course['faculty'].title().replace(' ', '_')) }

            # Remove other data - can look at appropriate mapping later if time permits
            del course['feeSummary']
            del course['entryRequirements']
            del course['aemCachedAt']

            self.add_node(course)
        for class_name in ['Person', 'Organisation', 'Grant', 'Collaboration', 'Publication']:
            self.create_class(class_name)
        
        for class_name in ['AcademicStaff', 'ResearchStudent']:
            self.create_class(class_name, 'Person')

        for class_name in ['Faculty', 'School', 'Institute']:
            self.create_class(class_name, 'Organisation')
        
        self.create_class('Thesis', 'Publication')

        self.create_property('affiliation', ['Person'], ['Organisation'])
        self.create_property('building', ['Person'], ['Organisation'])
        self.create_property('author', ['Person'], ['Publication'])
        self.create_property('grant', ['Person'], ['Grant'])
        self.create_property('collaboration', ['Person'], ['Collaboration'])

               for class_name in ['Campus', 'Building', 'Amenity']:
            self.create_class(class_name)

                    self.create_class('Event')

                     
self.create_property('campus', ['Building', 'Amenity'], ['Campus'])
self.create_property('building', ['Amenity', 'Person'], ['Building'])
import os, csv, re

def LoadProjects(filepath):
    with open(filepath, newline='') as csvfile:
        data = list(csv.reader(csvfile))
        return data

    return arr_projects

class ProjectName:
    RawName = ''
    Number = ''
    corridor = ''
    start = ''
    end = ''
    intersection_first_road = ''
    intersection_second_road = ''
    is_intersection = False
    has_errors = False
    def __init__(self, name, number):
        self.RawName = name.replace('_',' ')                            #remove any underscores if apparent
        self.Number = number
        self.split_name()
        self.integrity_check()
        if self.has_errors:
            print ('Errors for project: {}'.format(self.RawName))
        return

    def split_name(self):
        second_half_of_rawname = ''
        for char in ['&', ' and ', ' AND ', ' over ', ' OVER ']:        #Check if intersection
            if  self.RawName.find(char) > -1:
                self.is_intersection = True
                self.intersection_first_road = self.clean_name(self.RawName.split(char, 1)[0].strip())
                self.intersection_second_road = self.clean_name(self.RawName.split(char, 1)[1].strip())
                return
        for char in [',', ';']:                                         #find corridor
            if self.RawName.find(char) > -1:
                self.corridor = self.clean_name(self.RawName.split(char, 1)[0].strip())
                second_half_of_rawname = self.RawName.split(char, 1)[1].strip()
                break
        if second_half_of_rawname != '':
            for char in ['to', 'TO']:
                if second_half_of_rawname.find(char) > -1:
                    self.start = self.clean_name(second_half_of_rawname.split(char, 1)[0].strip())
                    self.end = self.clean_name(second_half_of_rawname.split(char, 1)[1].strip())
        return
    
    def integrity_check(self):
        if self.is_intersection:
            if ((self.intersection_first_road == '') or (self.intersection_second_road == '')):
                self.has_errors = True
        else:
            if ((self.corridor == '') or (self.start == '') or (self.end == '')):
                self.has_errors = True
        return
    
    def clean_name(self, street_name):

        index = {
            'Rd': ['rd', 'road'],
            'St': ['st', 'street'],
            'Way': ['way'],
            "walk": ['walk'],
            'Trl': ['trl', 'trail'],
            'Tpke': ['tpk', 'turnpike'],
            'Trce': ['trce', 'trace'],
            'Row': ['row'],
            'Pl': ['pl', 'place'],
            'Ln': ['ln', 'lane'],
            'Hwy': ['hwy', 'highway'],
            'Dr': ['dr', 'drive'],
            'Blvd': ['blvd', 'boulevard'],
            'Ave': ['ave', 'avenue']
        }

        for correct_suffix in index:
            for test_match in index[correct_suffix]:
                expression = test_match + r'\.?$'
                street_name = re.sub(expression, correct_suffix, street_name, 0, re.IGNORECASE)

        return street_name

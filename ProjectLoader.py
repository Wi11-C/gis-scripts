import os, csv, re

def LoadProjects(filepath):
    with open(filepath, newline='') as csvfile:
        data = list(csv.reader(csvfile))
    return data

class RoadName:
    full_name = ''
    corridor_prefix = ''
    corridor_name = ''
    corridor_type = ''
    corridor_suffix = ''

    def __init__(self, rawname):
        self.full_name = self.CleanType(rawname).upper()
        
        return
    
    def CleanType(self, street_name):

        index = {
            'rd': ['rd', 'road'],
            'st': ['st', 'street'],
            'way': ['way'],
            "walk": ['walk'],
            'trl': ['trl', 'trail'],
            'tpke': ['tpk', 'turnpike'],
            'trce': ['trce', 'trace'],
            'row': ['row'],
            'pl': ['pl', 'place'],
            'ln': ['ln', 'lane'],
            'hwy': ['hwy', 'highway'],
            'dr': ['dr', 'drive'],
            'blvd': ['blvd', 'boulevard'],
            'ave': ['ave', 'avenue']
        }

        for correct_suffix in index:
            for test_match in index[correct_suffix]:
                expression = test_match + r'\.?$'
                street_name = re.sub(expression, correct_suffix, street_name, 0, re.IGNORECASE)

        return street_name 
    
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
        for char in ['&', ' and ', ' AND ', ' over ', ' OVER ', ' at ', ' AT ', '@']:        #Check if intersection
            if  self.RawName.find(char) > -1:
                self.is_intersection = True
                self.intersection_first_road = RoadName(self.RawName.split(char, 1)[0].strip())
                self.intersection_second_road = RoadName(self.RawName.split(char, 1)[1].strip())
                return
        for char in [',', ';', ' from ', ' FROM ', ' FR ']:                                         #find corridor
            if self.RawName.find(char) > -1:
                self.corridor = RoadName(self.RawName.split(char, 1)[0].strip())
                second_half_of_rawname = self.RawName.split(char, 1)[1].strip()
                break
        if second_half_of_rawname != '':
            for char in [' to ', ' TO ']:
                if second_half_of_rawname.find(char) > -1:
                    self.start = RoadName(second_half_of_rawname.split(char, 1)[0].strip())
                    self.end = RoadName(second_half_of_rawname.split(char, 1)[1].strip())
        return
    
    def integrity_check(self):
        if self.is_intersection:
            if ((self.intersection_first_road == '') or (self.intersection_second_road == '')):
                self.has_errors = True
        else:
            if ((self.corridor == '') or (self.start == '') or (self.end == '')):
                self.has_errors = True
        return

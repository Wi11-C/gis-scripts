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
    is_intersection = False
    def __init__(self, name, number):
        self.RawName = name
        self.Number = number
        self.split_name()

    def split_name(self):
        second_half_of_rawname = ''
        for char in ['&', ' and ', ' AND ', ' over ', ' OVER ']:       #Check if intersection
            if self.RawName.find(char) > -1:
                self.is_intersection = True
                self.corridor = self.RawName.split(char, 1)[0].strip()
                self.start = self.RawName.split(char, 1)[1].strip()
                return
        for char in [',', ';']:         #find corrdior
            if self.RawName.find(char) > -1:
                self.corridor = self.RawName.split(char, 1)[0].strip()
                second_half_of_rawname = self.RawName.split(char, 1)[1].strip()
                break
        if second_half_of_rawname != '':
            for char in ['to', 'TO']:
                self.start = second_half_of_rawname.split(char, 1)[0].strip()
                self.end = second_half_of_rawname.split(char, 1)[1].strip()
        return
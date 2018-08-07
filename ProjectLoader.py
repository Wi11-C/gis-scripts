import os, csv, re

def LoadProjects(filepath):
    with open(filepath, newline='') as csvfile:
        data = list(csv.reader(csvfile))
        return data

    return arr_projects

class ProjectName:
    self.RawName = ''
    self.Number = ''
    self.corridor = ''
    self.start = ''
    self.end = ''
    self.is_intersection = False
    def __init__(self, name, number):
        self.RawName = name
        self.Number = number

    def split_name(self):
        self.corridor = self.RawName.split('.',1)[0]
        if self.corridor == '':
            self.corridor = self.RawName.split(';', 1)[0]
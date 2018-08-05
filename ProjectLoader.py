import os, csv

def LoadProjects(filepath):
    with open(filepath, 'r') as csvfile:
        data = list(csv.reader(csvfile))
        return data

    return arr_projects

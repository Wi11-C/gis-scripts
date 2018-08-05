import re

def correct_link(Link): #For some reason the links are stored as python paths with doubble slashes...which need to be changed to single slashes in the attribute field
    corrected_link = Link.replace('\\\\', '\\')
    return corrected_link

def get_proj_name_and_number_from_folder(folder):
    root, folder = os.path.split(folder)
    arr_folder_name = re.search(r'([a-zA-Z0-9]+)[\W|_]+([a-zA-Z0-9].+)',folder)
    proj_no = arr_folder_name[1].strip()
    proj_name = arr_folder_name[2].strip()
    return proj_no, proj_name

def get_sister_file_name(tif_file_path):
    sister_file_name = re.sub(r'.tif$', '.tfw', tif_file_path, 1, re.IGNORECASE)
    return sister_file_name

def get_sheet_no(tif_file_path):
    try:
        sheet_number = re.search(r'(?:sheet[\s|_]+)(\w+)', tif_file_path, re.IGNORECASE).group(0) #TODO: Get only sheet number
    except AttributeError:
        sheet_number = ''
        print ('No sheet number for the following file: ' + tif_file_path)
    return sheet_number

def get_proj_no(tif_file_path):
    proj_no = re.search(r'\w+', tif_file_path).group(0)
    return proj_no

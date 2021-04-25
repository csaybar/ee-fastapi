import os, re
from pathlib import Path
from typing import List

# Copy the token to the container
def load_credentials():
    ee_token = os.environ['EARTHENGINE_TOKEN']
    credential = '{"refresh_token":"%s"}' % ee_token
    credential_file_path = os.path.expanduser("~/.config/earthengine/")
    os.makedirs(credential_file_path,exist_ok=True)
    with open(credential_file_path + 'credentials', 'w') as file:
        file.write(credential)
    return True


def replace_line(file_name: str, line_num: int, text: str):
    """ Replace a specific line in a file

    Args:
        file_name (str): file path
        line_num (int): line to replace.
        text (str): Text to put in the line.

    Returns:
        bool: If the line was replaced will return True.
    """
    with open(file_name, 'r+') as f:
        lines = f.readlines()
        lines[line_num] = text
        f.writelines(lines)
    with open(file_name, 'w') as fw:    
        fw.writelines(lines)
    return True

def searching_all_files(path:str = ".", pattern : str="\.tiff$|\.csv$") -> List:
    dirpath = Path(path)
    assert(dirpath.is_dir())
    file_list = []
    for x in dirpath.iterdir():
        if x.is_file() and re.search(pattern, x.as_posix()):
            file_list.append(x.absolute().as_posix())
        elif x.is_dir():
            file_list.extend(searching_all_files(x, pattern))
    return file_list

def raster_to_vector(image, geom):
    vector_img = image.unmask(0).reduceToVectors(
        geometry = geom,
        scale = 10,
        bestEffort =True
    )
    return vector_img.getInfo()
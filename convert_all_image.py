from PIL import Image
from pix2tex.cli import LatexOCR

from os import listdir
from os.path import isfile, join, exists
import json

mypath = "./diagrams/diagrams/"

files = [f for f in listdir(mypath) if isfile(join(mypath, f))]

def convert_image(filepath):
    if not exists(filepath):
        return ""
    try:
        img = Image.open(filepath)
        model = LatexOCR()
        latex = model(img)
        if latex and str(latex) != "":
            return str(latex)
        else:
            return ""
    except Exception:
        pass
    return ""

def read_jsonl(path: str):
    with open(path) as f:
        data = json.load(f)
        return data

data = dict()
try:
    data = read_jsonl('converted_images.json')
    if(str(data) == ""):
        data = dict()
except Exception:
    data = dict()

for file in files:
    if file in data:
        continue
    print(join(mypath, file))
    converted = str(convert_image(join(mypath, file)))
    data[file] = converted
    with open('converted_images.json', 'w') as f:
        # write the dictionary to the file in JSON format
        json.dump(data, f)

from PIL import Image
from pix2tex.cli import LatexOCR

from os import listdir
from os.path import isfile, join, exists

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
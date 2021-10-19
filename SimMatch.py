import os
import imagehash
import shutil

from PIL import Image

image_hashs = []

def isSim(caimghash):

    for maimghash in image_hashs:
        if (1 - (maimghash - caimghash) / len(maimghash.hash) ** 2) > 0.90:
            return True
    
    return False

def hammingSim(caimghash):

    for maihimghash in image_hashs:
        num = 0
        for xidx in range(8):
            for yidx in range(8):
                if maihimghash.hash[xidx][yidx] != caimghash.hash[xidx][yidx]:
                    num += 1

        if (1 - num * 1.0 / 64) > 0.95:
            return True

    return False

for root, _, files in os.walk(r"D:\Code\CodeBehaiver\Auto-UIDump\UIDump\output\record"):

    for imgfile in files:
        if not imgfile.endswith("jpg"):
            continue
        imgpath = os.path.join(root, imgfile)
        imghash = imagehash.phash(Image.open(imgpath))

        if not hammingSim(imghash):
            image_hashs.append(imghash)
            print(imghash)
            shutil.copyfile(imgpath, os.path.join(r"D:\Code\CodeBehaiver\Auto-UIDump\UIDump\noOverLapSample", imgfile))
        
        
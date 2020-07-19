import os


def deleteFile(filepath):
    if os.path.exists(filepath):
        os.remove(filepath)

    pass
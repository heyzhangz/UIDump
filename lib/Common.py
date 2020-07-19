import os
import traceback


def deleteFile(filepath):
    if os.path.exists(filepath):
        os.remove(filepath)

    pass

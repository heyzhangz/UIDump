import json
import os


def deleteFile(filepath):
    if os.path.exists(filepath):
        os.remove(filepath)

    pass


def saveJsonFile(data, filepath):
    with open(filepath, "w", encoding='utf-8') as f:
        json.dump(data, f, indent=2)

    pass

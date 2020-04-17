import os, sys
import json
import xml.etree.ElementTree as ET
from collections import namedtuple

NodeInfo = namedtuple('NodeInfo', 'text, resid, clazz, desc')
AnnoInfo = namedtuple('AnnoInfo', 'category, words')

RecordBasePath = None
AnnoInfos = []
def parse_xml(xml):
    nodes = []
    for node in xml.iter('node'):
        attrib = node.attrib
        if attrib['text'] == '' and attrib['resource-id'] == '' and attrib['content-desc'] == '':
            continue
        resid = attrib['resource-id']
        if resid.startswith('com.android.systemui'):
            continue
        elif resid != '':
            resid = resid[resid.find('/')+1:]

        node = NodeInfo(attrib['text'], resid, attrib['class'], attrib['content-desc'])
        nodes.append(node)

    raw_words = set()
    for node in nodes:
        raw_words.add(node.text)
        raw_words.add(node.resid)
        raw_words.add(node.desc)
    #raw_words = [w.lower() for w in raw_words]
    raw_words = [w.lower() for w in raw_words]
    words = set()
    for raw_word in raw_words:
        if len(raw_word) > 50: continue #
        
        alpha_word = ''.join(x for x in raw_word if ord(x) < 256)

        alpha_word = "".join([c if c.isalpha() else ' ' for c in alpha_word])
        words.update(alpha_word.split(' '))

    Blacklist = ['', 'menu', 'btn', 'button', 'parent']
    rst_words = [w for w in words if w not in Blacklist ]

    print(len(words))
    print(words)
    print(len(rst_words))
    print(rst_words)
    return rst_words



def parse_record(record):
    apk_base_path = os.path.join(RecordBasePath, record)
    labels = None
    with open(os.path.join(apk_base_path, 'Label', 'label.json')) as label_file:
        labels = json.load(label_file)
    print(labels)

    for label in labels:
        layout_tree = ET.parse(os.path.join(apk_base_path, label['targetIndex'], 'layout.xml'))
        words = parse_xml(layout_tree)
        AnnoInfos.append(AnnoInfo(label['category'], words))

def read_annotations_files():

    dirs = os.listdir(RecordBasePath)

    for apk in dirs:
        print(apk)
        parse_record(apk)

    print(len(AnnoInfos))
    return AnnoInfos

if __name__ == '__main__':

    read_annotations_files()

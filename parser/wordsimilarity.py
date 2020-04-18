import IPython
from gensim.models.word2vec import Word2Vec
from gensim.models import KeyedVectors
import read_anno
import sys
import xml.etree.ElementTree as ET
import os
import json

photo_seed = ['photo', 'video', 'capture', 'shoot', 'record']
scan_qr_seed = ['scan', 'code']

def scen_similarity(xml, seeds):
    similar_words = []
    layout_tree = ET.parse(xml)
    xml_words = read_anno.parse_xml(layout_tree)
    for word in xml_words:
        if word not in model:
            continue
        for seed in seeds:
            similarity = model.similarity(word, seed)
            if similarity > 0.4:
                similar_words.append(word)
    return similar_words


def get_label_file(RecordBasePath):
    apk_base_path = RecordBasePath
    labels = None
    xml_trees = []
    with open(os.path.join(apk_base_path, 'Label', 'label.json')) as label_file:
        labels = json.load(label_file)
    for label in labels:
        layout_tree = os.path.join(apk_base_path, label['targetIndex'], 'layout.xml')
        xml_trees.append(layout_tree)
    return xml_trees


if __name__ == "__main__":
    print('load pre-trained model ... maybe it will cost 3 min')
    model = KeyedVectors.load_word2vec_format('../model/GoogleNews-vectors-negative300.bin', binary=True)

    record_path = sys.argv[1]
    pkg_list = []
    packages = os.listdir(record_path)
    for pkg in packages:
        pkg_list.append(os.path.join(record_path, pkg))
    IPython.embed()
    for pkg in pkg_list:
        trees = get_label_file(pkg)
        for tree in trees:
            photo_res = scen_similarity(tree, photo_seed)
            # print('Photo releated words: ' + res)
            qr_res = scen_similarity(tree, scan_qr_seed)
            print(tree)
            if len(photo_res) >= 1 and len(qr_res) >= 1:
                print('maybe photo or maybe qr')
            elif len(photo_res) >= 1 and len(qr_res) < 1:
                print('maybe photo')
            elif len(photo_res) < 1 and len(qr_res) >= 1:
                print('maybe qr')
            else:
                print('can not find any words ...')
            print('Photo releated words: ' )
            for word in photo_res:
                print(word)
            print('QR related words: ')
            for word in qr_res:
                print(word) 
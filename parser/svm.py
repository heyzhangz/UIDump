from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn import svm
import read_anno
import sys
import random

def gen_vector_from_bow(annos):
    texts = [' '.join(anno.words) for anno in annos  ]
    print(texts)
    cv = CountVectorizer()
    cv_fit = cv.fit_transform(texts)
    print(cv.vocabulary_)
    print(len(cv.vocabulary_))
    print(cv_fit.toarray())
#    print(cv_fit)
    return cv_fit.toarray()



if __name__ == "__main__":
    read_anno.RecordBasePath = sys.argv[1]
    annos = read_anno.read_annotations_files()
    print('-----------')
    print(len(annos))
    random.shuffle(annos) # Random annos list
    vectors = gen_vector_from_bow(annos)
    test_X , train_X = vectors[:10], vectors[10:]

    category_label = {}
    for anno in annos:
        if anno.category not in category_label:
            category_label[anno.category] = len(category_label)
    print(category_label)
    Y = []
    for anno in annos:
        Y.append(category_label[anno.category])
    test_Y , train_Y = Y[:10], Y[10:]

    clf = svm.SVC(decision_function_shape='ovo')
    clf.fit(train_X, train_Y)
#    for i in range(10):
#        print('id {} : label {} predict {}'.format(i, test_Y[i], clf.predict(test_X[i])))
    print(test_Y)
    predict_res = clf.predict(test_X)
    print(type(predict_res))
    for i in range(10):
        print('id {} : label {} predict {}'.format(i, test_Y[i], predict_res[i]))
    score = clf.score(test_X, test_Y)

    print("score {}".format(score))

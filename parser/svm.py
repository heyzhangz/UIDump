from sklearn.feature_extraction.text import CountVectorizer
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
    test_set , train_set = vectors[:10], vectors[10:]
    clf = svm.SVC(decision_function_shape='ovo')

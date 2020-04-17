from sklearn.feature_extraction.text import CountVectorizer
import read_anno
import sys

def gen_vector_from_bow(annos):
    texts = [' '.join(anno.words) for anno in annos  ]
    print(texts)
    cv = CountVectorizer()
    cv_fit = cv.fit_transform(texts)
    print(cv.vocabulary_)
    print(len(cv.vocabulary_))
    print(cv_fit.toarray())
    print(cv_fit)



if __name__ == "__main__":
    read_anno.RecordBasePath = sys.argv[1]
    annos = read_anno.read_annotations_files()
    print('-----------')
    print(len(annos))
    print(annos[2])
    gen_vector_from_bow(annos)

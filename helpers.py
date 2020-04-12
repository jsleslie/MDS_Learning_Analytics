import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from gensim import corpora
from gensim import models
from gensim import similarities

stop_words = stopwords.words('english')
### Helper functions for app.py
def convert_csv_to_list(posts_df):
    """[summary]
    
    Arguments:
        posts_df {[type]} -- [description]
    """
    # take only the combined column
    posts_df = posts_df["combined"]

    # Convert the column to a list
    corpus_text = list()
    for row in range(posts_df.shape[0]):
        temp = posts_df.iloc[row]
        corpus_text.append(temp)

    # Convert the list to list of lists
    processed_corpus = list()

    stem_sentence = []
    porter = PorterStemmer()

    for text in corpus_text:

        token_words = word_tokenize(text)
        token_words
        stem_sentence = []
        for word in token_words:
            stem_sentence.append(porter.stem(word))
            stem_sentence.append(" ")
#         # tokenize it
#         tokenized_list = word_tokenize(text)

        # convert to lower case
        tokenized_list = [w.lower() for w in stem_sentence]

        # get the alphabetic words
        words = [word for word in tokenized_list if word.isalpha()]

        # get rid of stop words
        words = [w for w in words if not w in stop_words]

        processed_corpus.append(words)

    return processed_corpus  # list of lists


def train_model(corpus):
    """[summary]
    
    Arguments:
        corpus {[type]} -- [description]
    
    Returns:
        [type] -- [description]
    """
    dictionary_reddit = corpora.Dictionary(corpus)
    num_words = len(dictionary_reddit.keys())

    # convert to a bag of words reprensentation
    bow_corpus_reddit = [dictionary_reddit.doc2bow(text) for text in corpus]

    # train the model
    tfidf_reddit = models.TfidfModel(bow_corpus_reddit)

    # similarities model
    index_reddit = similarities.SparseMatrixSimilarity(tfidf_reddit[bow_corpus_reddit],
                                                       num_features=num_words)
    return index_reddit, dictionary_reddit, tfidf_reddit


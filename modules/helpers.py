import re
import unidecode
import numpy as np
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer


def clean_text(text):
    '''
    Convert text to all lowercase and strip it of natural line breaks, non-
    unicode characters, punctuations, numbers, unwanted regex patterns, and
    stopwords, then lemmatize nouns and verbs.

    Args:
    text: a string.

    Returns:
    A cleaned text string.
    '''

    bad_regex = [r'\([a-z].*?\d\)', r'\S+.com', r'\d+', r'[^\w\s]', 'score']
    stop_words = stopwords.words('english')
    wnl = WordNetLemmatizer()

    text = text.lower()
    text = ' '.join(text.splitlines())  # remove natural line breaks
    text = unidecode.unidecode(text)  # remove non-English characters
    text = re.sub('|'.join(bad_regex), '', text) # remove unwanted regex patterns

    tokens = word_tokenize(text)
    tokens = [wnl.lemmatize(token) for token in tokens if token not in stop_words]  # lemmatize and remove stopwords
    text = ' '.join(tokens)

    return text

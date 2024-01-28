import os
import re
import nltk
import spacy
import unicodedata
from nltk.corpus import wordnet
from nltk.tokenize.toktok import ToktokTokenizer

from constants import SP_PIPELINES_DIR_MAP
from contractions import CONTRACTION_MAP

tokenizer = ToktokTokenizer()


def configure_spacy(_language):
    pipeline = SP_PIPELINES_DIR_MAP.get(
        _language
    )
    if not pipeline:
        raise ValueError('Sorry! we only support English, Polish and Russian')
    return spacy.load(pipeline)


def extract_original_text(lang):
    _dir = os.path.join('dataset', f'{lang}/')
    for i, filename in enumerate(os.listdir(_dir), start=1):
        file_path = os.path.join(_dir, filename)

        def _text_token_tuple(_line):
            _l = _line.split('\t')
            return (_l[0], _l[1]) if len(_l) > 2 else None

        with open(file_path, 'r', encoding='utf-8') as file:
            filtered_list = list(
                filter(None, map(
                    _text_token_tuple, file.readlines()
                ))
            )
            result = ''
            prev_token_type, prev_token = None, None
            for token_type, token in filtered_list:
                no_space = (token_type == 'PUNCT' and token in [',', '.']) \
                           or prev_token in ['"', '('] or \
                           (prev_token == '.' and token in ['"', '(', "'"]
                            )
                no_space |= prev_token_type == 'PLAIN' and token in ['"', "'", ")"]
                result += token if no_space else ' ' + token
                prev_token_type, prev_token = token_type, token
            result = result.lstrip()
            print(f"Extracted Original Text: {result}")
            return result


def _tokenize_text(text):
    print("Tokenizing...")
    print("Generating Tokens....")
    tokens = tokenizer.tokenize(text)
    tokens = [token.strip() for token in tokens]
    print(f"Tokens: {tokens}")
    print("Tokenization Complete.")
    return tokens


def simple_porter_stemming(text):
    ps = nltk.porter.PorterStemmer()
    text = ' '.join([ps.stem(word) for word in text.split()])
    return text


def lemmatize_text(text, lang):
    nlp = configure_spacy(lang)
    text = nlp(text)
    text = ' '.join([word.lemma_ if word.lemma_ != '-PRON-' else word.text for word in text])
    return text


def remove_repeated_characters(tokens):
    repeat_pattern = re.compile(r'(\w*)(\w)\2(\w*)')
    match_substitution = r'\1\2\3'

    def replace(old_word):
        if wordnet.synsets(old_word):
            return old_word
        new_word = repeat_pattern.sub(match_substitution, old_word)
        return replace(new_word) if new_word != old_word else new_word

    correct_tokens = [replace(word) for word in tokens]
    return correct_tokens


def expand_contractions(text, contraction_mapping=CONTRACTION_MAP):
    contractions_pattern = re.compile('({})'.format('|'.join(contraction_mapping.keys())),
                                      flags=re.IGNORECASE | re.DOTALL)

    def expand_match(contraction):
        match = contraction.group(0)
        first_char = match[0]
        expanded_contraction = contraction_mapping.get(match) \
            if contraction_mapping.get(match) \
            else contraction_mapping.get(match.lower())
        expanded_contraction = first_char + expanded_contraction[1:]
        return expanded_contraction

    expanded_text = contractions_pattern.sub(expand_match, text)
    expanded_text = re.sub("'", "", expanded_text)
    return expanded_text


def remove_accented_chars(text):
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8', 'ignore')
    return text


def remove_special_characters(text, remove_digits=False):
    pattern = r'[^a-zA-Z0-9\s]|\[|\]' if not remove_digits else r'[^a-zA-Z\s]|\[|\]'
    text = re.sub(pattern, '', text)
    return text


def remove_stopwords(text, is_lower_case=False):
    stopwords = nltk.corpus.stopwords.words('english')
    tokens = tokenizer.tokenize(text)
    tokens = [token.strip() for token in tokens]
    if is_lower_case:
        filtered_tokens = [token for token in tokens if token not in stopwords]
    else:
        filtered_tokens = [token for token in tokens if token.lower() not in stopwords]
    filtered_text = ' '.join(filtered_tokens)
    return filtered_text

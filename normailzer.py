from constants import ENGLISH, POLISH, RUSSIAN, LANGUAGE_DIRECTORY_MAPPING

from helpers import *


def normalize_text(lang, contraction_expansion=True,
                   accented_char_removal=True, text_lower_case=True,
                   text_stemming=True, text_lemmatization=True,
                   special_char_removal=True, remove_digits=True,
                   stopword_removal=True):
    from helpers import _tokenize_text
    stemmed_text = []
    lemmatized_text = []
    normalized_text = []
    # normalize paragraph and print it out
    _dir = LANGUAGE_DIRECTORY_MAPPING.get(
        lang
    )
    paragraph = extract_original_text(lang)
    tokenized_text = _tokenize_text(paragraph)
    for text in tokenized_text:
        # remove accented characters
        if accented_char_removal:
            text = remove_accented_chars(text)

        # expand contractions
        if contraction_expansion:
            text = expand_contractions(text)

        # lemmatize text
        if text_lemmatization:
            text = lemmatize_text(text, lang)
            lemmatized_text.append(text)

        # stem text
        if text_stemming and not text_lemmatization:
            text = simple_porter_stemming(text)
            stemmed_text.append(stemmed_text)

        # remove special characters and\or digits
        if special_char_removal:
            # insert spaces between special characters to isolate them
            special_char_pattern = re.compile(
                r'([{.(-)!}])'
            )
            text = special_char_pattern.sub(" \\1 ", text)
            text = remove_special_characters(text, remove_digits=remove_digits)

            # remove extra whitespace
        text = re.sub(' +', ' ', text)

        if text_lower_case:
            text = text.lower()

        # remove stopwords
        if stopword_removal:
            text = remove_stopwords(
                text, is_lower_case=text_lower_case
            )

        text = re.sub(' +', ' ', text)
        text = text.strip()
        if text:
            normalized_text.append(text)
    print(f"Lemmatized Text:{lemmatized_text}")
    print(f"Stemmed Text:{lemmatized_text}")
    return normalized_text


if __name__ == '__main__':
    text_to_be_normalized = [ENGLISH, POLISH, RUSSIAN]
    print('Starting Process...')
    normalized_text = normalize_text(ENGLISH)
    print(f"Normalized Text: {normalized_text}")
    print('Normalization Complete.')


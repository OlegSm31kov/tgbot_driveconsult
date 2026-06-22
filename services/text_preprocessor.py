from natasha import (
    Segmenter,
    MorphVocab,
    NewsEmbedding,
    NewsMorphTagger,
    Doc
)

from ru_word2number import w2n
import re

segmenter = Segmenter()
morph_vocab = MorphVocab()

emb = NewsEmbedding()
morph_tagger = NewsMorphTagger(emb)


def lemmatize(text: str) -> str:
    doc = Doc(text.lower())

    doc.segment(segmenter)
    doc.tag_morph(morph_tagger)

    lemmas = []

    for token in doc.tokens:
        token.lemmatize(morph_vocab)
        lemmas.append(token.lemma)

    return " ".join(lemmas)


NUMBER_WORDS = {
    "ноль", "один", "два", "три", "четыре",
    "пять", "шесть", "семь", "восемь", "девять",
    "десять", "одиннадцать", "двенадцать",
    "тринадцать", "четырнадцать", "пятнадцать",
    "шестнадцать", "семнадцать", "восемнадцать",
    "девятнадцать", "двадцать", "тридцать",
    "сорок", "пятьдесят", "шестьдесят",
    "семьдесят", "восемьдесят", "девяносто",
    "сто", "двести", "триста", "четыреста",
    "пятьсот", "шестьсот", "семьсот",
    "восемьсот", "девятьсот",
    "тысяча", "миллион"
}


def replace_number_words(text: str) -> str:
    words = text.split()
    result = []

    i = 0
    while i < len(words):

        if words[i] not in NUMBER_WORDS:
            result.append(words[i])
            i += 1
            continue

        j = i

        while j < len(words) and words[j] in NUMBER_WORDS:
            j += 1

        phrase = " ".join(words[i:j])

        try:
            number = w2n.word_to_num(phrase)

            if number is not None:
                result.append(str(number))
            else:
                result.extend(words[i:j])

        except Exception:
            result.extend(words[i:j])

        i = j

    return " ".join(result)


def preprocess(text: str) -> str:
    text = text.lower()
    text = lemmatize(text)
    text = replace_number_words(text)
    return text
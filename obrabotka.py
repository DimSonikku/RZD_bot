import pdfplumber
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize
import pymorphy2
import string

morph = pymorphy2.MorphAnalyzer()
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('stopwords')
stop_words = set(stopwords.words('russian'))

def extract_text_from_pdf(file_path):
    with pdfplumber.open(file_path) as pdf:
        text = ''
        for page in pdf.pages:
            text += page.extract_text()
    return text

# Функция для лемматизации предложения
def lemmatize_sentence(sentence):
    tokens = word_tokenize(sentence)
    tokens = [word for word in tokens if word.lower() not in stop_words and word not in string.punctuation]
    lemmas = [morph.parse(token)[0].normal_form for token in tokens]
    return lemmas

def process_text(question, file_path):
    text = str(extract_text_from_pdf(file_path))
    # Токенизация на предложения
    sentences = sent_tokenize(text)
    lemmatized_sentences = []

    for i in range(len(sentences)):
      lemmatized_sentences.append(lemmatize_sentence(sentences[i]))

    # Токенизация вопроса (разделение на слова)
    tokens = word_tokenize(question)

    # Удаляем стоп-слова (предлоги, местоимения и прочие малозначительные слова)
    filtered_tokens = [word for word in tokens if (word.lower() not in stop_words and word.lower() not in string.punctuation)]
    # Извлечение ключевых существительных и глаголов
    keywords = []
    for token in filtered_tokens:
        parsed = morph.parse(token)[0]  # Лемматизация и получение первой интерпретации
        keywords.append(parsed.normal_form)  # Добавляем лемму (нормальную форму слова)
    keywords = [word for word in keywords if word not in string.punctuation]

    references = ""

    for i in range(len(keywords)):
      num = 1
      references += f"\nСовпадения для слова: {keywords[i]}\n"
      references += "----------------------------------------------\n"
      for j in range(len(sentences)):
        if keywords[i] in lemmatized_sentences[j]:
            references += f"{num}: \n{sentences[j]}\n"
            num += 1
      references += "----------------------------------------------\n\n"

    return references
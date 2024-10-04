import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus.reader.plaintext import PlaintextCorpusReader
from nltk.corpus import stopwords, wordnet
from nltk.stem import WordNetLemmatizer
import string
import os
from Scraping import scrape_document


url = "https://webscraper.io/test-sites/e-commerce/static"
output_file = "document.txt"

# Scrape the document and read the contents
scrape_document(url, output_file)

# Read the scraped document
with open(output_file, 'r') as file:
    texts = file.read()

# Split the text into individual lines
texts = texts.splitlines()

# Step 1: Tokenization and Preprocessing
tokenized_texts = []
stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

for text in texts:
    # Tokenize into words
    words = word_tokenize(text)

    # Normalize (lowercase, remove punctuation, remove stopwords, lemmatize)
    normalized_words = []
    for word in words:
        # Convert to lowercase
        word = word.lower()

        # Remove punctuation
        word = word.translate(str.maketrans('', '', string.punctuation))

        # Remove stopwords and empty strings
        if word not in stop_words and word.strip():
            # Lemmatize the word
            word = lemmatizer.lemmatize(word)
            normalized_words.append(word)

    # Join normalized words back into a sentence (optional)
    normalized_text = " ".join(normalized_words)
    tokenized_texts.append(normalized_text)

# Step 2: Organize and Save Corpus
corpus_dir = 'my_custom_corpus'
if not os.path.exists(corpus_dir):
    os.makedirs(corpus_dir)

# Write tokenized texts to separate files in the corpus directory
for i, text in enumerate(tokenized_texts):
    with open(os.path.join(corpus_dir, f'doc{i + 1}.txt'), 'w', encoding='utf-8') as file:
        file.write(text)

# Step 3: Create an NLTK Corpus Reader
corpus = PlaintextCorpusReader(corpus_dir, '.*\.txt')
print("Words in the corpus:")
print(corpus.words())
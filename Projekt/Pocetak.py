import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer  # Import WordNetLemmatizer for lemmatization
import string
import os
from Scraping_soup import scrape_document

url = "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
output_file = "document.txt"
final_corpus_file = "final_corpus.txt"  # File to save all words

# Scrape the document and read the contents
scrape_document(url, output_file)

# Read the scraped document
with open(output_file, 'r') as file:
    texts = file.read()

# Split the text into individual lines
texts = texts.splitlines()

# Step 1: Tokenization and Preprocessing
all_normalized_words = []  # List to hold all normalized words
stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()  # Initialize the WordNet Lemmatizer

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

    # Add normalized words to the overall list
    all_normalized_words.extend(normalized_words)

# Step 2: Save all normalized words to a single text file
with open(final_corpus_file, 'w', encoding='utf-8') as file:
    for word in all_normalized_words:
        file.write(f"{word}\n")  # Write each word on a new line
print(f"Final corpus saved to '{final_corpus_file}' with each word on a new line.")
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import string
import os
import re
from gensim.models import Word2Vec
from Scraping_spacy import scrape_document

# Ensure necessary NLTK resources are downloaded (uncomment if needed)
# nltk.download('punkt')
# nltk.download('stopwords')
# nltk.download('wordnet')

def is_emoji(s):
    """Check if a string contains an emoji."""
    return bool(re.search(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F700-\U0001F77F\U0001F900-\U0001F9FF\U00002700-\U000027BF]', s))

def preprocess_text(texts):
    """Tokenizes, removes stopwords, lemmatizes words, and filters out numbers and emojis."""
    all_normalized_words = []
    stop_words = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()

    for text in texts:
        words = word_tokenize(text)
        normalized_words = [
            lemmatizer.lemmatize(word.lower().translate(str.maketrans('', '', string.punctuation)))
            for word in words if word.isalpha() and word.lower() not in stop_words and not is_emoji(word) and not word.isdigit()
        ]
        if normalized_words:  # Only append non-empty lists
            all_normalized_words.append(normalized_words)

    print(f"Preprocessed {len(all_normalized_words)} sentences.")  # Debug print
    return all_normalized_words

def save_corpus(corpus, filename):
    """Saves normalized words to a text file in the Corpus directory."""
    # Ensure the Corpus directory exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    with open(filename, 'a', encoding='utf-8') as file:  # Change 'w' to 'a' to append
        for sentence in corpus:
            line = " ".join(sentence)  # Join words in each sentence with spaces
            file.write(line + "\n")  # Save each sentence on a new line

    print(f"Corpus appended to '{filename}' with {len(corpus)} sentences.")  # Debug print

def main():
    url = input("Please enter the URL of the website to scrape: ")
    website_name = url.split("//")[-1].split("/")[0]  # Extract domain name from URL

    # Define fixed filename for the model and dynamic filename for the corpus
    fixed_model_file = "word2vec.model"
    final_corpus_file = f"Corpus/{website_name}_corpus.txt"  # Save corpus in Corpus directory
    output_file = "document.txt"

    try:
        scrape_document(url, output_file)
    except Exception as e:
        print(f"Error scraping document: {e}")
        return

    with open(output_file, 'r', encoding='utf-8') as file:
        texts = file.read().splitlines()

    print(f"Scraped {len(texts)} lines from '{output_file}'.")  # Debug print
    print("Sample scraped text:", texts[:5])  # Print first 5 lines for inspection

    all_normalized_words = preprocess_text(texts)

    # Prepare sentences for Word2Vec
    sentences_for_w2v = all_normalized_words

    # Load existing model or create a new one if it doesn't exist
    if os.path.exists(fixed_model_file):
        model = Word2Vec.load(fixed_model_file)
        print("Loaded existing Word2Vec model.")
        model.build_vocab(sentences_for_w2v, update=True)  # Update vocabulary with new sentences
        model.train(sentences_for_w2v, total_examples=model.corpus_count, epochs=model.epochs)
    else:
        model = Word2Vec(sentences=sentences_for_w2v, vector_size=100, window=5, min_count=1, workers=4)
        print("Created new Word2Vec model.")

    # Save the updated model and append to the corpus file
    model.save(fixed_model_file)
    save_corpus(sentences_for_w2v, final_corpus_file)

    print(f"Word2Vec model saved to '{fixed_model_file}'.")

    # Cleanup temporary files if necessary
    os.remove(output_file)

if __name__ == '__main__':
    main()
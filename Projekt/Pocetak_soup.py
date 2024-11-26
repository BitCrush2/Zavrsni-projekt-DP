import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import string
import os
from gensim.models import Word2Vec
from Scraping_soup import scrape_document


# Ensure necessary NLTK resources are downloaded (uncomment if needed)
# nltk.download('punkt')
# nltk.download('stopwords')
# nltk.download('wordnet')

def preprocess_text(texts):
    """Tokenizes, removes stopwords, and lemmatizes words in the given texts."""
    all_normalized_words = []
    stop_words = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()

    for text in texts:
        words = word_tokenize(text)
        normalized_words = [
            lemmatizer.lemmatize(word.lower().translate(str.maketrans('', '', string.punctuation)))
            for word in words if word.lower() not in stop_words and word.strip()
        ]
        all_normalized_words.append(normalized_words)  # Append as a sentence

    return all_normalized_words


def save_corpus(corpus, filename):
    """Saves normalized words to a text file."""
    with open(filename, 'w', encoding='utf-8') as file:
        for sentence in corpus:
            file.write(" ".join(sentence) + "\n")  # Save each sentence on a new line


def main():
    url = input("Please enter the URL of the website to scrape: ")
    website_name = url.split("//")[-1].split("/")[0]  # Extract domain name from URL

    # Define fixed filename for the model and dynamic filename for the corpus
    fixed_model_file = "word2vec.model"
    final_corpus_file = f"{website_name}_corpus.txt"  # Use website name for corpus
    output_file = "document.txt"

    try:
        scrape_document(url, output_file)
    except Exception as e:
        print(f"Error scraping document: {e}")
        return

    with open(output_file, 'r', encoding='utf-8') as file:
        texts = file.read().splitlines()

    all_normalized_words = preprocess_text(texts)

    # Prepare sentences for Word2Vec
    sentences_for_w2v = all_normalized_words

    model = Word2Vec(sentences=sentences_for_w2v, vector_size=100, window=5, min_count=1, workers=4)

    # Save using fixed model filename and dynamic corpus filename
    model.save(fixed_model_file)
    save_corpus(sentences_for_w2v, final_corpus_file)

    print(f"Final corpus saved to '{final_corpus_file}' with each sentence on a new line.")
    print(f"Word2Vec model saved to '{fixed_model_file}'.")

    # Cleanup temporary files if necessary
    os.remove(output_file)


if __name__ == '__main__':
    main()
from gensim.models import Word2Vec


def load_model(model_file):
    """Load the Word2Vec model from a file."""
    try:
        model = Word2Vec.load(model_file)
        print(f"Model '{model_file}' loaded successfully.")
        return model
    except Exception as e:
        print(f"Error loading model: {e}")
        return None


def check_most_similar(model):
    """Find and display the most similar words for a given word using the loaded model."""
    while True:
        word = input("Enter a word to find its most similar words (or type 'exit' to quit): ").strip()
        if word.lower() == 'exit':
            break

        if not word:
            print("Input must be non-empty. Please try again.")
            continue

        # Check if the word is in vocabulary
        if word not in model.wv.key_to_index:
            print(f"'{word}' is not in the vocabulary.")
            continue

        # Get most similar words
        try:
            similar_words = model.wv.most_similar(word, topn=5)  # Get top 5 most similar words
            print(f"Most similar words to '{word}':")
            for similar_word, similarity in similar_words:
                print(f"{similar_word}: {similarity:.4f}")
        except Exception as e:
            print(f"Error retrieving similar words: {e}")


def main():
    model_file = "word2vec.model"  # Ensure this matches your saved model filename
    model = load_model(model_file)
    words = list(model.wv.key_to_index.keys())
    #print(f"Total words in the model: {len(words)}")
    #for word in words:
        #print(word)
    if model is not None:
        check_most_similar(model)


if __name__ == '__main__':
    main()
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


def check_similarity(model):
    """Check similarity between two words using the loaded model."""
    while True:
        word1 = input("Enter the first word (or type 'exit' to quit): ")
        if word1.lower() == 'exit':
            break
        word2 = input("Enter the second word: ")

        try:
            similarity = model.wv.similarity(word1, word2)
            print(f"Similarity between '{word1}' and '{word2}': {similarity:.4f}")
        except KeyError as e:
            print(f"One of the words is not in the vocabulary: {e}")


def main():
    model_file = "word2vec.model"  # Ensure this matches your saved model filename
    model = load_model(model_file)

    if model is not None:
        check_similarity(model)


if __name__ == '__main__':
    main()
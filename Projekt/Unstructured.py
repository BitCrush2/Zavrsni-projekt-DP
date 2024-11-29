import os
from transformers import pipeline
from unstructured.partition.text import partition_text
from Scraping_soup import scrape_document
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Download NLTK resources (only need to run once)
# nltk.download('punkt')
# nltk.download('stopwords')

# Initialize stopwords
stop_words = set(stopwords.words('english'))


def clean_text(text):
    """Clean and preprocess the input text."""
    # Tokenize the text
    tokens = word_tokenize(text)

    # Remove stopwords and keep full words
    cleaned_tokens = [
        token.lower()  # Convert to lowercase
        for token in tokens
        if token.isalnum() and token.lower() not in stop_words
    ]

    # Join the cleaned tokens back into a string
    return ' '.join(cleaned_tokens)


# Get user input for the URL
url = input("Please enter the URL of the website to scrape: ")

# Scrape the document from the provided URL
scrape_document(url, "output1.txt")
document_text = "output1.txt"

if os.path.exists(document_text):
    # Partition the scraped text into structured elements
    elements = partition_text(document_text)

    # Create a new directory named 'Corpus_unstructured'
    folder_name = "Corpus_unstructured"
    os.makedirs(folder_name, exist_ok=True)  # Create folder if it doesn't exist

    # Extract the base name from the URL for naming the text file
    website_name = url.split("//")[-1].split("/")[0]  # Get domain name from URL
    corpus_file_name = os.path.join(folder_name, f"{website_name}.txt")  # Create full path for corpus file

    # Save the structured elements to a corpus file with cleaned text
    cleaned_texts = []  # List to hold all cleaned texts

    with open(corpus_file_name, "w", encoding="utf-8") as f:
        for element in elements:
            cleaned_text = clean_text(element.text)
            cleaned_texts.append(cleaned_text)  # Add cleaned text to list
            f.write(f"{cleaned_text}\n\n")  # Write each cleaned element with a newline for separation

    print(f"Corpus created successfully and saved to '{corpus_file_name}'.")

    # Load sentiment analysis model
    sentiment_analyzer = pipeline("sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment")

    # Load named entity recognition model
    ner_model = pipeline("ner", aggregation_strategy="simple", model="dbmdz/bert-large-cased-finetuned-conll03-english")

    # Analyze each cleaned text line by line
    for cleaned_text in cleaned_texts:
        if len(cleaned_text) > 30:  # Ensure text is longer than 30 characters

            # Sentiment Analysis
            try:
                sentiment = sentiment_analyzer(cleaned_text)
                print(f"Sentiment for line: {cleaned_text}\nSentiment: {sentiment}\n")
            except Exception as e:
                print(f"Error during sentiment analysis: {e}")

            # Named Entity Recognition (NER)
            try:
                entities = ner_model(cleaned_text)
                print("Named Entities for line:")
                for entity in entities:
                    print(f"- {entity['word']} ({entity['entity_group']})")
                print("\n")
            except Exception as e:
                print(f"Error during NER: {e}")

else:
    print("Failed to scrape any content from the provided URL.")

# Clean up by removing the temporary output file
os.remove("output1.txt")
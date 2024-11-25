import requests
import spacy
from spacy_html_tokenizer import create_html_tokenizer

def scrape_document(url, output_file):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raises an HTTPError for bad responses
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return

    # Load spaCy model and set up HTML tokenizer
    nlp = spacy.blank("en")  # Create a blank English model
    nlp.tokenizer = create_html_tokenizer()(nlp)  # Use HTML tokenizer

    # Process the HTML content with spaCy
    doc = nlp(response.text)

    # Open the output file in write mode
    with open(output_file, 'w', encoding='utf-8') as file:
        # Write each sentence to the file
        for sent in doc.sents:
            file.write(sent.text + '\n')

# Example usage
# scrape_document('https://example.com', 'output.txt')
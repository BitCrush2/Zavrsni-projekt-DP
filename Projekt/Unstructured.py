import requests
from unstructured.partition.text import partition_text
from Scraping_soup import scrape_document

# Get user input for the URL
url = input("Please enter the URL of the website to scrape: ")

# Scrape the document
scrape_document(url,"output1.txt")
document_text="output1.txt"

if document_text:
    # Partition the scraped text into structured elements
    elements = partition_text(document_text)

    # Save the structured elements to a corpus file
    with open("corpus.txt", "w", encoding="utf-8") as f:
        for element in elements:
            f.write(f"{element.text}\n\n")  # Write each element with a newline for separation

    print("Corpus created successfully and saved to 'corpus.txt'.")
else:
    print("Failed to scrape any content from the provided URL.")
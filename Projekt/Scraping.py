import requests
from bs4 import BeautifulSoup

def scrape_document(url, output_file):
    # Send a GET request to the URL
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code != 200:
        print(f"Failed to retrieve the document. Status code: {response.status_code}")
        return

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all paragraph tags in the HTML
    paragraphs = soup.find_all('p')

    # Open the output file in write mode
    with open(output_file, 'w') as file:
        # Write each paragraph to the file
        for paragraph in paragraphs:
            file.write(paragraph.get_text() + '\n')
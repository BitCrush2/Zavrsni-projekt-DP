import requests
from bs4 import BeautifulSoup

def scrape_document(url, output_file):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raises an HTTPError for bad responses
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return

    soup = BeautifulSoup(response.content, 'html.parser')
    paragraphs = soup.find_all('p')

    with open(output_file, 'w', encoding='utf-8') as file:
        for paragraph in paragraphs:
            file.write(paragraph.get_text() + '\n')

# Example usage
# scrape_document('https://example.com', 'output.txt')
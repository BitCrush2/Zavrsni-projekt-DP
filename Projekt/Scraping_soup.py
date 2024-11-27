import requests
from bs4 import BeautifulSoup


def scrape_document(url, output_file):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raises an HTTPError for bad responses
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return

    soup = BeautifulSoup(response.content, 'html.parser')

    # Remove header and footer elements
    for header in soup.find_all('header'):
        header.decompose()  # Remove header elements
    for footer in soup.find_all('footer'):
        footer.decompose()  # Remove footer elements

    # Extract the main content from the body
    body_content = soup.find('body')

    # Check if body_content is found
    if body_content:
        # Write all text from the body to the output file, excluding headers and footers
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(body_content.get_text(separator='\n', strip=True))
    else:
        print("No body content found.")

# Example usage
# scrape_document('https://example.com', 'output.txt')
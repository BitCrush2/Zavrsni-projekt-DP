import os
import re
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup

# Replace with your actual SerpAPI key
SERPAPI_KEY = '817cb3c86c656b2cf733db9f39410a40b6e091be0ce782a9e80ff9fba8850f06'


def sanitize_filename(filename):
    """Sanitize the filename by removing invalid characters."""
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    sanitized = sanitized.strip('. ')
    return sanitized[:100]


def search_articles(query, page):
    """Search for articles using Google SERP API."""
    url = "https://serpapi.com/search"
    params = {
        'q': query,
        'engine': 'google',
        'api_key': SERPAPI_KEY,
        'start': (page - 1) * 10  # Pagination
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json().get('organic_results', [])
    except Exception as e:
        print(f"API Error: {e}")
        return []


def find_pdf_links(article_url):
    """Scan the article page for PDF links."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(article_url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all links ending with .pdf
        pdf_links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.lower().endswith('.pdf'):
                # Handle relative URLs
                if not href.startswith('http'):
                    href = requests.compat.urljoin(article_url, href)
                pdf_links.append(href)
        return pdf_links
    except Exception as e:
        print(f"Error scanning {article_url}: {e}")
        return []


def download_pdf(pdf_url, filename):
    """Download a PDF and validate its content."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(pdf_url, headers=headers, stream=True, timeout=10)
        response.raise_for_status()

        # Validate content type (ensure it's a PDF)
        content_type = response.headers.get('Content-Type', '')
        if 'application/pdf' not in content_type:
            print(f"Invalid content type ({content_type}) for URL: {pdf_url}")
            return

        # Save the PDF
        with open(filename, 'wb') as f:
            for chunk in tqdm(response.iter_content(chunk_size=1024), desc=f"Downloading {filename}"):
                if chunk:
                    f.write(chunk)

        # Verify the downloaded file is a PDF
        with open(filename, 'rb') as f:
            header = f.read(4)
            if header != b'%PDF':
                print(f"Downloaded file is not a valid PDF: {filename}")
                os.remove(filename)
        print(f"Successfully saved: {filename}")

    except Exception as e:
        print(f"Download failed: {e}")
        if os.path.exists(filename):
            os.remove(filename)  # Delete corrupted files


def main():
    if not os.path.exists('scholar_pdf'):
        os.makedirs('scholar_pdf')

    # User input
    keywords = input("Enter keywords (comma-separated): ").strip().split(',')
    keywords = [k.strip() for k in keywords if k.strip()]
    if not keywords:
        print("No valid keywords provided.")
        return

    try:
        num_pages = int(input("Number of pages to search (1 page = 10 results): ").strip())
        if num_pages < 1:
            raise ValueError
    except ValueError:
        print("Invalid number of pages. Using default (1).")
        num_pages = 1

    # Process keywords
    for keyword in keywords:
        print(f"\nSearching for articles related to: {keyword}")
        for page in range(1, num_pages + 1):
            print(f"Page {page}:")
            articles = search_articles(keyword, page)
            if not articles:
                print("No articles found.")
                break

            for article in articles:
                article_url = article.get('link')
                print(f"Scanning article: {article_url}")
                pdf_links = find_pdf_links(article_url)

                if not pdf_links:
                    print("No PDF links found on this page.")
                    continue

                for pdf_url in pdf_links:
                    title = sanitize_filename(article.get('title', 'untitled'))
                    filename = os.path.join('scholar_pdf', f"{title}.pdf")

                    if os.path.exists(filename):
                        print(f"Skipping existing file: {filename}")
                        continue

                    download_pdf(pdf_url, filename)


if __name__ == "__main__":
    main()
import os
import re
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup

# Make sure you install scholarly via:
# pip install scholarly

def sanitize_filename(filename):
    """Sanitize the filename by removing invalid characters."""
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    sanitized = sanitized.strip('. ')
    return sanitized[:100] if sanitized else "untitled"

def search_articles(query, page):
    """
    Search for articles using the scholarly package to query Google Scholar.
    This function paginates results (10 per page).
    """
    from scholarly import scholarly
    results = []
    start = (page - 1) * 10
    end = start + 10
    for i, pub in enumerate(scholarly.search_pubs(query)):
        if i < start:
            continue
        if i >= end:
            break
        results.append(pub)
    return results

def find_pdf_links(article_url):
    """Scan the article page for PDF links."""
    headers = {
        'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/91.0.4472.124 Safari/537.36')
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
        'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/91.0.4472.124 Safari/537.36')
    }
    try:
        response = requests.get(pdf_url, headers=headers, stream=True, timeout=10)
        response.raise_for_status()

        # Validate content type (ensure it's a PDF)
        content_type = response.headers.get('Content-Type', '').lower()
        if 'application/pdf' not in content_type:
            print(f"Invalid content type ({content_type}) for URL: {pdf_url}")
            return

        # Save the PDF with a progress bar
        with open(filename, 'wb') as f:
            for chunk in tqdm(response.iter_content(chunk_size=1024),
                              desc=f"Downloading {filename}"):
                if chunk:
                    f.write(chunk)

        # Verify the downloaded file is a PDF by checking its header
        with open(filename, 'rb') as f:
            header = f.read(4)
            if header != b'%PDF':
                print(f"Downloaded file is not a valid PDF: {filename}")
                os.remove(filename)
                return
        print(f"Successfully saved: {filename}")

    except Exception as e:
        print(f"Download failed for {pdf_url}: {e}")
        if os.path.exists(filename):
            os.remove(filename)

def main():
    if not os.path.exists('scholar_pdf'):
        os.makedirs('scholar_pdf')

    # User input for keywords and number of pages
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

    # Process each keyword
    for keyword in keywords:
        print(f"\nSearching for articles related to: {keyword}")
        for page in range(1, num_pages + 1):
            print(f"Page {page}:")
            articles = search_articles(keyword, page)
            if not articles:
                print("No articles found.")
                break

            for pub in articles:
                # Determine article URL from the publication data
                article_url = pub.get('pub_url') or pub['bib'].get('url')
                if not article_url:
                    print("No valid article link found; skipping.")
                    continue

                print(f"Scanning article: {article_url}")
                pdf_links = find_pdf_links(article_url)
                if not pdf_links:
                    print("No PDF links found on this page.")
                    continue

                # If multiple PDFs are found, append an index to differentiate filenames
                for idx, pdf_url in enumerate(pdf_links, start=1):
                    base_title = sanitize_filename(pub['bib'].get('title', 'untitled'))
                    title = f"{base_title}_{idx}" if len(pdf_links) > 1 else base_title
                    filename = os.path.join('scholar_pdf', f"{title}.pdf")

                    if os.path.exists(filename):
                        print(f"Skipping existing file: {filename}")
                        continue

                    download_pdf(pdf_url, filename)

if __name__ == "__main__":
    main()

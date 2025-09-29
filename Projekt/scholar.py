import os
import re
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup
from scholarly import scholarly
from urllib.parse import urljoin

# Define a constant header to mimic a real browser in HTTP requests.
HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/91.0.4472.124 Safari/537.36'
    )
}


def sanitize_filename(filename):
    """
    Sanitize the filename by removing characters that are not allowed
    in file names and trimming its length to a maximum of 100 characters.
    """
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename).strip('. ')
    return sanitized[:100] if sanitized else "untitled"


def search_articles(query, page):
    """
    Use the scholarly package to search for publications based on the query.

    Pagination: Returns 10 results per page.

    Parameters:
        query (str): The search keywords.
        page (int): Which page of results to return.

    Returns:
        List of publication records (dictionaries).
    """
    results = []
    start = (page - 1) * 10  # Calculate starting index
    end = start + 10  # Ending index (exclusive)
    for i, pub in enumerate(scholarly.search_pubs(query)):
        if i < start:
            continue
        if i >= end:
            break
        results.append(pub)
    return results


def find_pdf_links(article_url):
    """
    Download the HTML content of the given article URL and scan for PDF links
    by checking all <a href> tags for URLs that end with '.pdf'.

    Parameters:
        article_url (str): The URL of the article page.

    Returns:
        List of PDF URLs found on the page.
    """
    try:
        response = requests.get(article_url, headers=HEADERS, timeout=10)
        response.raise_for_status()  # Raise an error for bad status codes
        soup = BeautifulSoup(response.text, 'html.parser')
        pdf_links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.lower().endswith('.pdf'):
                # Convert relative URL to absolute URL if needed.
                if not href.startswith('http'):
                    href = urljoin(article_url, href)
                pdf_links.append(href)
        return pdf_links
    except Exception as e:
        print(f"Error scanning {article_url}: {e}")
        return []


def download_pdf(pdf_url, filename):
    """
    Download the PDF from the given URL and save it to the specified filename.

    This function uses a progress bar to show download progress and verifies
    that the downloaded file is a valid PDF (by checking its header).

    Parameters:
        pdf_url (str): The direct URL to the PDF.
        filename (str): The local filename to save the PDF.
    """
    try:
        response = requests.get(pdf_url, headers=HEADERS, stream=True, timeout=10)
        response.raise_for_status()

        # Verify the response's Content-Type is that of a PDF.
        content_type = response.headers.get('Content-Type', '').lower()
        if 'application/pdf' not in content_type:
            print(f"Invalid content type ({content_type}) for URL: {pdf_url}")
            return

        # Write the content to the file in chunks, with a progress bar.
        with open(filename, 'wb') as f:
            for chunk in tqdm(response.iter_content(chunk_size=1024),
                              desc=f"Downloading {os.path.basename(filename)}"):
                if chunk:
                    f.write(chunk)

        # Open the saved file and check if it starts with '%PDF'
        with open(filename, 'rb') as f:
            if f.read(4) != b'%PDF':
                print(f"Downloaded file is not a valid PDF: {filename}")
                os.remove(filename)
                return

        print(f"Successfully saved: {filename}")

    except Exception as e:
        print(f"Download failed for {pdf_url}: {e}")
        if os.path.exists(filename):
            os.remove(filename)


def main():
    """
    Main function to search for PDFs based on user-specified keywords.

    For each publication:
      1. Check if a direct PDF link is available in the metadata.
      2. If not, load the article page and search its <a href> tags for a PDF link.
      3. Download the PDF to a local folder named 'pdfs'.
    """
    # Create the output directory if it doesn't exist.
    output_dir = 'pdfs'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Get keywords from the user (comma-separated).
    keywords = input("Enter keywords (comma-separated): ").strip().split(',')
    keywords = [k.strip() for k in keywords if k.strip()]
    if not keywords:
        print("No valid keywords provided.")
        return

    # Get the number of pages to search (each page has 10 results).
    try:
        num_pages = int(input("Number of pages to search (1 page = 10 results): ").strip())
        if num_pages < 1:
            raise ValueError
    except ValueError:
        print("Invalid number of pages. Using default (1).")
        num_pages = 1

    # Process each keyword.
    for keyword in keywords:
        print(f"\nSearching for PDF results related to: {keyword}")
        for page in range(1, num_pages + 1):
            print(f"\n--- Page {page} ---")
            results = search_articles(keyword, page)
            if not results:
                print("No results found.")
                break

            for pub in results:
                bib = pub.get('bib', {})
                pdf_url = None

                # Attempt to get a direct PDF URL from common metadata fields.
                for key in ['pub_url', 'url', 'eprint']:
                    candidate = pub.get(key) or bib.get(key)
                    if candidate and candidate.lower().endswith('.pdf'):
                        pdf_url = candidate
                        break

                # If no direct PDF URL is found, scan the article page for PDF links.
                if not pdf_url:
                    article_url = pub.get('pub_url') or bib.get('url')
                    if article_url:
                        links = find_pdf_links(article_url)
                        if links:
                            pdf_url = links[0]  # Use the first PDF link found.
                            print(f"Found PDF via scanning: {pdf_url}")
                        else:
                            print("No PDF links found on the page.")
                            continue
                    else:
                        print("No valid article URL available; skipping result.")
                        continue

                # Prepare a filename using the publication's title.
                title = sanitize_filename(bib.get('title', 'untitled'))
                filename = os.path.join(output_dir, f"{title}.pdf")
                if os.path.exists(filename):
                    print(f"Skipping existing file: {filename}")
                    continue

                print(f"Downloading PDF from: {pdf_url}")
                download_pdf(pdf_url, filename)


if __name__ == "__main__":
    main()

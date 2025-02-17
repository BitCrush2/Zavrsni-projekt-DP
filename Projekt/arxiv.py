import os
import re
import requests
import feedparser
import urllib.parse

def sanitize_filename(filename):
    # Remove characters that are not allowed in filenames (common restrictions)
    sanitized = re.sub(r'[\\/*?:"<>|]', "", filename)
    return sanitized.strip()

def download_pdf(pdf_url, file_path):
    try:
        response = requests.get(pdf_url)
        response.raise_for_status()  # Check for HTTP errors
        with open(file_path, "wb") as f:
            f.write(response.content)
        print(f"Downloaded: {file_path}")
    except Exception as e:
        print(f"Failed to download {pdf_url}: {e}")

def main():
    # Get search keywords and number of pages from user
    keywords = input("Enter search keywords: ")
    try:
        num_pages = int(input("Enter number of pages to search: "))
    except ValueError:
        print("Please enter a valid number for pages.")
        return

    results_per_page = 10  # Each page returns 10 results
    base_url = "http://export.arxiv.org/api/query?"

    # Create the folder to save PDFs if it doesn't exist
    os.makedirs("arxiv_pdf", exist_ok=True)

    # URL encode the keywords
    encoded_keywords = urllib.parse.quote(keywords)

    for page in range(num_pages):
        start = page * results_per_page
        query_url = (f"{base_url}search_query=all:{encoded_keywords}"
                     f"&start={start}&max_results={results_per_page}")
        print(f"\nSearching page {page + 1}: {query_url}")

        # Parse the Atom feed returned by arXiv
        feed = feedparser.parse(query_url)
        if 'entries' not in feed or not feed.entries:
            print("No results found on this page.")
            continue

        for entry in feed.entries:
            pdf_url = None
            # Look for the PDF link in the entry's links
            for link in entry.links:
                if hasattr(link, "type") and link.type == "application/pdf":
                    pdf_url = link.href
                    break

            if pdf_url:
                # Use the title of the paper for the filename, and sanitize it.
                title = entry.title if 'title' in entry else "untitled"
                safe_title = sanitize_filename(title)
                file_path = os.path.join("arxiv_pdf", f"{safe_title}.pdf")
                print(f"Downloading PDF for paper titled: {title}...")
                download_pdf(pdf_url, file_path)
            else:
                print("No PDF link found for this entry.")

if __name__ == "__main__":
    main()

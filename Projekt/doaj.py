
import os
import re
import requests
from bs4 import BeautifulSoup

# DOAJ API base URL (Directory of Open Access Journals)
DOAJ_API_BASE_URL = "https://doaj.org/api/search/"


def search_doaj(search_type, search_term, page=1, page_size=10, api_key=None):
    """
    Search the DOAJ API for journals or articles.

    Parameters:
        search_type (str): Type of search - 'journals' or 'articles'
        search_term (str): Search query string
        page (int): Pagination page number (default: 1)
        page_size (int): Number of results per page (default: 10)
        api_key (str): Optional API key for authenticated requests

    Returns:
        dict: JSON response from API or None if error occurs
    """
    # Set request headers with API key if provided
    headers = {"Accept": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    # Construct API URL with parameters
    url = f"{DOAJ_API_BASE_URL}{search_type}/{search_term}?page={page}&pageSize={page_size}"

    try:
        # Make GET request to DOAJ API
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise exception for HTTP errors
        return response.json()  # Return parsed JSON response
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"An error occurred: {err}")
    return None


def download_pdf(url, save_path):
    """
    Download a PDF file from a given URL and save to specified path.

    Parameters:
        url (str): Direct URL to PDF file
        save_path (str): Local file path to save PDF
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for HTTP errors

        # Write PDF content to file in binary mode
        with open(save_path, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded PDF: {save_path}")
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred while downloading {url}: {http_err}")
    except Exception as err:
        print(f"An error occurred while downloading {url}: {err}")


def get_article_pdf_link(article_url):
    """
    Extract PDF download link from article page by parsing HTML.

    Parameters:
        article_url (str): URL to article's landing page

    Returns:
        str: Direct URL to PDF or None if not found
    """
    try:
        response = requests.get(article_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Strategy 1: Look for MDPI-style PDF links (common in some journals)
        pdf_link = soup.find('a', class_='pdf-link')
        if pdf_link and pdf_link.get('href'):
            return pdf_link['href']

        # Strategy 2: Look for text-based PDF links (e.g., 'PDF' button)
        pdf_link = soup.find('a', text='PDF')
        if pdf_link and pdf_link.get('href'):
            return pdf_link['href']

        # If no PDF link found through common patterns
        print(f"No PDF link found on {article_url}")
        return None

    except Exception as err:
        print(f"Error fetching PDF link from {article_url}: {err}")
        return None


def display_results(search_type, search_results):
    """
    Display search results in a readable format.

    Parameters:
        search_type (str): Type of results ('journals' or 'articles')
        search_results (dict): API response containing results
    """
    print(f"Found {len(search_results['results'])} {search_type}:")

    for i, item in enumerate(search_results['results'], start=1):
        bibjson = item.get('bibjson', {})

        if search_type == "journals":
            # Journal information display
            print(f"- Title: {bibjson.get('title', 'N/A')}")
            # Extract both print and electronic ISSN numbers
            issns = [issn.get('value', 'N/A') for issn in bibjson.get('identifier', [])
                     if issn.get('type') in ['pissn', 'eissn']]
            print(f"  ISSN: {', '.join(issns)}")
            print(f"  Publisher: {bibjson.get('publisher', 'N/A')}")
            # Find journal homepage URL
            journal_links = [link.get('url') for link in bibjson.get('link', [])
                             if link.get('type') == 'homepage']
            print(f"  Journal Link: {journal_links[0] if journal_links else 'Not available'}")
        else:  # Article results
            # Article information display
            print(f"{i}. Title: {bibjson.get('title', 'N/A')}")
            # Extract DOI identifiers
            dois = [identifier.get('id', 'N/A') for identifier in bibjson.get('identifier', [])
                    if identifier.get('type') == 'doi']
            print(f"   DOI: {', '.join(dois)}")
            print(f"   Journal: {bibjson.get('journal', {}).get('title', 'N/A')}")
            # Show abstract (shortened in actual display)
            print(f"   Abstract: {bibjson.get('abstract', 'N/A')}")
            # Find fulltext link and try to get PDF URL
            article_links = [link.get('url') for link in bibjson.get('link', [])
                             if link.get('type') == 'fulltext']
            if article_links:
                pdf_link = get_article_pdf_link(article_links[0])
                print(f"   Full-text PDF URL: {pdf_link if pdf_link else 'Not available'}")
            else:
                print("   Article Link: Not available")
        print()  # Add spacing between items


def sanitize_filename(title):
    """
    Clean article title to create safe filenames by removing invalid characters.

    Parameters:
        title (str): Original article title

    Returns:
        str: Sanitized filename-safe string
    """
    # Replace problematic filesystem characters with underscores
    sanitized_title = re.sub(r'[\\/*?:"<>|]', "_", title)
    return sanitized_title.strip()


def download_articles(search_results, download_dir):
    """
    Download PDFs for all articles in search results to specified directory.

    Parameters:
        search_results (dict): API response containing articles
        download_dir (str): Directory to save downloaded PDFs
    """
    for i, item in enumerate(search_results['results'], start=1):
        bibjson = item.get('bibjson', {})
        # Find fulltext links from API response
        article_links = [link.get('url') for link in bibjson.get('link', [])
                         if link.get('type') == 'fulltext']

        if article_links:
            # Get direct PDF link from article page
            pdf_link = get_article_pdf_link(article_links[0])
            if pdf_link:
                # Create safe filename from title
                title = bibjson.get('title', f'article_{i}')
                sanitized_title = sanitize_filename(title)
                save_path = os.path.join(download_dir, f"{sanitized_title}.pdf")
                download_pdf(pdf_link, save_path)
            else:
                print(f"No PDF available for article {i}: {bibjson.get('title', 'N/A')}")
        else:
            print(f"No article link available for article {i}: {bibjson.get('title', 'N/A')}")


def main():
    """Main function to handle user interaction and workflow."""
    # Get user input for search type
    search_type = input("Do you want to search for 'journals' or 'articles'? ").strip().lower()
    if search_type not in ["journals", "articles"]:
        print("Invalid search type. Please choose 'journals' or 'articles'.")
        return

    # Get search term from user
    search_term = input(f"Enter search term for {search_type}: ").strip()
    if not search_term:
        print("Search term cannot be empty.")
        return

    # Optional API key input
    api_key = input("Enter your DOAJ API key (optional): ").strip() or None

    # Perform search
    search_results = search_doaj(search_type, search_term, api_key=api_key)
    if not search_results or 'results' not in search_results:
        print("No results found.")
        return

    # Display results to user
    display_results(search_type, search_results)

    # Handle PDF downloads for articles
    if search_type == "articles":
        download_dir = "pdfs"  # Default download directory
        os.makedirs(download_dir, exist_ok=True)  # Create directory if needed
        download_articles(search_results, download_dir)


if __name__ == "__main__":
    main()
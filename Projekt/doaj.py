import os
import requests
from bs4 import BeautifulSoup

# DOAJ API base URL
DOAJ_API_BASE_URL = "https://doaj.org/api/search/"

def search_doaj(search_type, search_term, page=1, page_size=10, api_key=None):
    headers = {"Accept": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    url = f"{DOAJ_API_BASE_URL}{search_type}/{search_term}?page={page}&pageSize={page_size}"

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"An error occurred: {err}")
    return None

def download_pdf(url, save_path):
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(save_path, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded PDF: {save_path}")
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred while downloading {url}: {http_err}")
    except Exception as err:
        print(f"An error occurred while downloading {url}: {err}")

def get_article_pdf_link(article_url):
    try:
        response = requests.get(article_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        pdf_link = soup.find('a', class_='pdf-link')['href']
        return pdf_link
    except Exception as err:
        print(f"Error fetching PDF link from {article_url}: {err}")
    return None

def display_results(search_type, search_results):
    print(f"Found {len(search_results['results'])} {search_type}:")
    for i, item in enumerate(search_results['results'], start=1):
        bibjson = item.get('bibjson', {})
        if search_type == "journals":
            print(f"- Title: {bibjson.get('title', 'N/A')}")
            print(f"  ISSN: {', '.join(issn.get('value', 'N/A') for issn in bibjson.get('identifier', []) if issn.get('type') in ['pissn', 'eissn'])}")
            print(f"  Publisher: {bibjson.get('publisher', 'N/A')}")
            journal_links = [link.get('url') for link in bibjson.get('link', []) if link.get('type') == 'homepage']
            print(f"  Journal Link: {journal_links[0] if journal_links else 'Not available'}")
        else:  # articles
            print(f"{i}. Title: {bibjson.get('title', 'N/A')}")
            print(f"   DOI: {', '.join(identifier.get('id', 'N/A') for identifier in bibjson.get('identifier', []) if identifier.get('type') == 'doi')}")
            print(f"   Journal: {bibjson.get('journal', {}).get('title', 'N/A')}")
            print(f"   Abstract: {bibjson.get('abstract', 'N/A')}")
            article_links = [link.get('url') for link in bibjson.get('link', []) if link.get('type') == 'fulltext']
            if article_links:
                pdf_link = get_article_pdf_link(article_links[0])
                print(f"   Full-text PDF URL: {pdf_link if pdf_link else 'Not available'}")
            else:
                print("   Article Link: Not available")
        print()

def download_articles(search_results, download_dir):
    for i, item in enumerate(search_results['results'], start=1):
        bibjson = item.get('bibjson', {})
        article_links = [link.get('url') for link in bibjson.get('link', []) if link.get('type') == 'fulltext']
        if article_links:
            pdf_link = get_article_pdf_link(article_links[0])
            if pdf_link:
                save_path = os.path.join(download_dir, f"article_{i}.pdf")
                download_pdf(pdf_link, save_path)
            else:
                print(f"No PDF available for article {i}: {bibjson.get('title', 'N/A')}")
        else:
            print(f"No article link available for article {i}: {bibjson.get('title', 'N/A')}")

def main():
    search_type = input("Do you want to search for 'journals' or 'articles'? ").strip().lower()
    if search_type not in ["journals", "articles"]:
        print("Invalid search type. Please choose 'journals' or 'articles'.")
        return

    search_term = input(f"Enter search term for {search_type}: ").strip()
    if not search_term:
        print("Search term cannot be empty.")
        return

    api_key = input("Enter your DOAJ API key (optional): ").strip() or None

    search_results = search_doaj(search_type, search_term, api_key=api_key)
    if not search_results or 'results' not in search_results:
        print("No results found.")
        return

    display_results(search_type, search_results)

    if search_type == "articles":
        download_choice = input("Do you want to download available PDFs? (yes/no): ").strip().lower()
        if download_choice == 'yes':
            download_dir = "doaj_pdf"
            os.makedirs(download_dir, exist_ok=True)
            download_articles(search_results, download_dir)

if __name__ == "__main__":
    main()
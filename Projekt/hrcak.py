import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def download_pdf(url, folder_name, file_name):
    """
    Download a PDF file from a given URL and save it to a specified folder with a custom filename.

    Parameters:
        url (str): The URL of the PDF file to download.
        folder_name (str): The directory where the PDF will be saved.
        file_name (str): The name of the PDF file (without extension).

    Returns:
        str: The path to the downloaded PDF file, or None if the download fails.
    """
    response = requests.get(url)
    if response.status_code == 200:
        # Create a valid filename by replacing special characters
        safe_file_name = "".join(c if c.isalnum() or c in " -_" else "_" for c in file_name)
        pdf_path = os.path.join(folder_name, f"{safe_file_name}.pdf")
        with open(pdf_path, 'wb') as pdf_file:
            pdf_file.write(response.content)
        print(f"Downloaded: {pdf_path}")
        return pdf_path
    else:
        print(f"Failed to download: {url}")
        return None

def extract_details_from_page(page_url):
    """
    Extract the title, abstract, and keywords from a given page URL.

    Parameters:
        page_url (str): The URL of the page to extract information from.

    Returns:
        tuple: A tuple containing title, abstract, and keywords.
    """
    response = requests.get(page_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract the title (assume it is within a <h1> or <title> tag)
    title = soup.find('h1') or soup.find('title')
    title_text = title.get_text(strip=True) if title else "No title found"

    # Extract the abstract (usually inside a <div> or <p> tag with a specific class)
    abstract = soup.find('meta', attrs={'name': 'description'})
    abstract_text = abstract.get('content', "No abstract found") if abstract else "No abstract found"

    # Extract keywords (usually in a meta tag with name='keywords')
    keywords = soup.find('meta', attrs={'name': 'keywords'})
    keywords_text = keywords.get('content', "No keywords found") if keywords else "No keywords found"

    return title_text, abstract_text, keywords_text

def save_details_to_file(title, abstract, keywords, folder_name="metadata"):
    """
    Save the extracted details (title, abstract, keywords) into a text file.

    Parameters:
        title (str): The title of the page.
        abstract (str): The abstract of the page.
        keywords (str): The keywords of the page.
        folder_name (str): The folder to save the text files in.
    """
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    # Create a valid filename by replacing special characters
    safe_file_name = "".join(c if c.isalnum() or c in " -_" else "_" for c in title[:50])
    file_name = os.path.join(folder_name, f"{safe_file_name}.txt")
    with open(file_name, 'w', encoding='utf-8') as file:
        file.write(f"Title: {title}\n")
        file.write(f"Abstract: {abstract}\n")
        file.write(f"Keywords: {keywords}\n")

    print(f"Details saved to: {file_name}")

def scrape_pdfs_from_website(base_url, keyword, num_pages, folder_name="pdfs"):
    """
    Scrape PDF files from a website based on a search keyword, and extract information from each result page.

    Parameters:
        base_url (str): The base URL of the website to scrape.
        keyword (str): The keyword to search for.
        num_pages (int): The number of search result pages to scrape.
        folder_name (str): The directory to save downloaded PDFs (default: "pdfs").
    """
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    for page_num in range(num_pages):
        start = page_num * 10
        search_url = f"{base_url}/pretraga?q={keyword}&start={start}"
        print(f"Scraping page: {search_url}")

        response = requests.get(search_url)
        soup = BeautifulSoup(response.content, 'html.parser')

        for link in soup.find_all('h5'):
            article_link = link.find('a', href=True)
            if article_link:
                article_url = urljoin(base_url, article_link['href'])
                print(f"Found article page: {article_url}")

                # Extract metadata from the article page
                title, abstract, keywords = extract_details_from_page(article_url)

                # Save metadata to a text file
                save_details_to_file(title, abstract, keywords)

                # Find the PDF link on the article page
                article_response = requests.get(article_url)
                article_soup = BeautifulSoup(article_response.content, 'html.parser')
                pdf_link = article_soup.find('a', class_='btn btn-outline-primary btn-sm', href=True)

                if pdf_link:
                    pdf_url = urljoin(base_url, pdf_link['href'])
                    print(f"Found PDF link: {pdf_url}")

                    # Download the PDF and save it with the title as the filename
                    download_pdf(pdf_url, folder_name, title)

if __name__ == "__main__":
    base_url = "https://hrcak.srce.hr"
    keyword = input("Enter the keyword to search for: ")
    num_pages = int(input("Enter the number of pages to scrape: "))
    scrape_pdfs_from_website(base_url, keyword, num_pages)
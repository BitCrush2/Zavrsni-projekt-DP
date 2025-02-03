import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from PyPDF2 import PdfReader

def download_pdf(url, folder_name):
    response = requests.get(url)
    if response.status_code == 200:
        # Extract the file ID from the URL to use as the PDF name
        file_id = url.split('/')[-1]
        pdf_name = os.path.join(folder_name, f"{file_id}.pdf")
        with open(pdf_name, 'wb') as pdf_file:
            pdf_file.write(response.content)
        print(f"Downloaded: {pdf_name}")
        return pdf_name
    else:
        print(f"Failed to download: {url}")
        return None

def extract_text_from_pdf(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")
        return None

def scrape_pdfs_from_website(base_url, keyword, num_pages, folder_name="pdfs"):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    for page_num in range(num_pages):
        start = page_num * 10  # Increment start by 10 for each page
        search_url = f"{base_url}/pretraga?q={keyword}&start={start}"
        print(f"Scraping page: {search_url}")
        response = requests.get(search_url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all <a> tags with href attributes
        for link in soup.find_all('a', href=True):
            href = link['href']
            # Check if the link points to a PDF (assume /file/ indicates a PDF)
            if "/file/" in href:
                # Construct the full URL for the PDF
                pdf_url = urljoin(base_url, href)
                print(f"Found PDF link: {pdf_url}")
                pdf_path = download_pdf(pdf_url, folder_name)
                if pdf_path:
                    text = extract_text_from_pdf(pdf_path)
                    if text:
                        print(f"Extracted text from {pdf_path}:\n{text[:200]}...\n")  # Print first 200 chars

if __name__ == "__main__":
    base_url = "https://hrcak.srce.hr"
    keyword = input("Enter the keyword to search for (e.g., medicine): ")
    num_pages = int(input("Enter the number of pages to scrape (each page increments by 10): "))
    scrape_pdfs_from_website(base_url, keyword, num_pages)
# Import required libraries
import os  # For file and directory operations
import requests  # For making HTTP requests
from bs4 import BeautifulSoup  # For parsing HTML content
from urllib.parse import urljoin  # For constructing absolute URLs from relative paths
from PyPDF2 import PdfReader  # For extracting text from PDF files


def download_pdf(url, folder_name):
    """
    Download a PDF file from a given URL and save it to a specified folder.

    Parameters:
        url (str): The URL of the PDF file to download.
        folder_name (str): The directory where the PDF will be saved.

    Returns:
        str: The path to the downloaded PDF file, or None if the download fails.
    """
    # Send a GET request to the PDF URL
    response = requests.get(url)

    # Check if the request was successful (HTTP status code 200)
    if response.status_code == 200:
        # Extract the file ID from the URL to use as the PDF filename
        file_id = url.split('/')[-1]

        # Create the full path for saving the PDF
        pdf_name = os.path.join(folder_name, f"{file_id}.pdf")

        # Save the PDF content to the specified file
        with open(pdf_name, 'wb') as pdf_file:
            pdf_file.write(response.content)

        print(f"Downloaded: {pdf_name}")
        return pdf_name
    else:
        # Print an error message if the download fails
        print(f"Failed to download: {url}")
        return None


def extract_text_from_pdf(pdf_path):
    """
    Extract text content from a PDF file.

    Parameters:
        pdf_path (str): The path to the PDF file.

    Returns:
        str: The extracted text, or None if an error occurs.
    """
    try:
        # Initialize a PDF reader object
        reader = PdfReader(pdf_path)
        text = ""

        # Iterate through each page in the PDF and extract text
        for page in reader.pages:
            text += page.extract_text()

        return text
    except Exception as e:
        # Handle any errors that occur during text extraction
        print(f"Error extracting text from {pdf_path}: {e}")
        return None


def scrape_pdfs_from_website(base_url, keyword, num_pages, folder_name="pdfs"):
    """
    Scrape PDF files from a website based on a search keyword.

    Parameters:
        base_url (str): The base URL of the website to scrape.
        keyword (str): The keyword to search for.
        num_pages (int): The number of search result pages to scrape.
        folder_name (str): The directory to save downloaded PDFs (default: "pdfs").
    """
    # Create the folder if it doesn't already exist
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    # Iterate through the specified number of search result pages
    for page_num in range(num_pages):
        # Calculate the start parameter for pagination (increments of 10)
        start = page_num * 10

        # Construct the search URL with the keyword and pagination
        search_url = f"{base_url}/pretraga?q={keyword}&start={start}"
        print(f"Scraping page: {search_url}")

        # Send a GET request to the search URL
        response = requests.get(search_url)

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all <a> tags with href attributes
        for link in soup.find_all('a', href=True):
            href = link['href']

            # Check if the link points to a PDF (assume "/file/" indicates a PDF)
            if "/file/" in href:
                # Construct the full URL for the PDF using the base URL
                pdf_url = urljoin(base_url, href)
                print(f"Found PDF link: {pdf_url}")

                # Download the PDF and save it to the specified folder
                pdf_path = download_pdf(pdf_url, folder_name)

                # If the PDF is successfully downloaded, extract text from it
                if pdf_path:
                    text = extract_text_from_pdf(pdf_path)

                    # Print the first 200 characters of the extracted text
                    if text:
                        print(f"Extracted text from {pdf_path}:\n{text[:200]}...\n")


if __name__ == "__main__":
    # Base URL of the website to scrape
    base_url = "https://hrcak.srce.hr"

    # Prompt the user for a keyword to search for
    keyword = input("Enter the keyword to search for: ")

    # Prompt the user for the number of pages to scrape
    num_pages = int(input("Enter the number of pages to scrape: "))

    # Start the scraping process
    scrape_pdfs_from_website(base_url, keyword, num_pages)
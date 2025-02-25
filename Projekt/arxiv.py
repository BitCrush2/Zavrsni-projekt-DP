# Import required libraries
import os  # For file and directory operations
import re  # For regular expressions (filename sanitization)
import requests  # For making HTTP requests
import feedparser  # For parsing Atom/RSS feeds
import urllib.parse  # For URL encoding


def sanitize_filename(filename):
    """
    Sanitize a filename by removing invalid characters.

    Parameters:
        filename (str): The original filename.

    Returns:
        str: A sanitized filename safe for use in file systems.
    """
    # Remove characters that are not allowed in filenames (common restrictions)
    sanitized = re.sub(r'[\\/*?:"<>|]', "", filename)
    return sanitized.strip()


def download_pdf(pdf_url, file_path):
    """
    Download a PDF file from a given URL and save it to a specified path.

    Parameters:
        pdf_url (str): The URL of the PDF file to download.
        file_path (str): The local path where the PDF will be saved.
    """
    try:
        # Send a GET request to the PDF URL
        response = requests.get(pdf_url)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Save the PDF content to the specified file
        with open(file_path, "wb") as f:
            f.write(response.content)
        print(f"Downloaded: {file_path}")
    except Exception as e:
        # Handle any errors that occur during the download
        print(f"Failed to download {pdf_url}: {e}")


def main():
    """
    Main function to handle user interaction and workflow.
    """
    # Get search keywords from the user
    keywords = input("Enter search keywords: ")

    # Get the number of pages to search from the user
    try:
        num_pages = int(input("Enter number of pages to search: "))
    except ValueError:
        # Handle invalid input (non-integer values)
        print("Please enter a valid number for pages.")
        return

    results_per_page = 10  # Each page returns 10 results
    base_url = "http://export.arxiv.org/api/query?"  # Base URL for arXiv API

    # Create the folder to save PDFs if it doesn't exist
    os.makedirs("arxiv_pdf", exist_ok=True)

    # URL encode the keywords to ensure they are safe for use in URLs
    encoded_keywords = urllib.parse.quote(keywords)

    # Iterate through the specified number of pages
    for page in range(num_pages):
        # Calculate the start parameter for pagination
        start = page * results_per_page

        # Construct the query URL for the arXiv API
        query_url = (f"{base_url}search_query=all:{encoded_keywords}"
                     f"&start={start}&max_results={results_per_page}")
        print(f"\nSearching page {page + 1}: {query_url}")

        # Parse the Atom feed returned by arXiv
        feed = feedparser.parse(query_url)

        # Check if the feed contains any entries
        if 'entries' not in feed or not feed.entries:
            print("No results found on this page.")
            continue

        # Iterate through each entry in the feed
        for entry in feed.entries:
            pdf_url = None

            # Look for the PDF link in the entry's links
            for link in entry.links:
                if hasattr(link, "type") and link.type == "application/pdf":
                    pdf_url = link.href
                    break

            if pdf_url:
                # Use the title of the paper for the filename
                title = entry.title if 'title' in entry else "untitled"

                # Sanitize the title to create a safe filename
                safe_title = sanitize_filename(title)

                # Construct the full file path for saving the PDF
                file_path = os.path.join("arxiv_pdf", f"{safe_title}.pdf")

                # Download the PDF
                print(f"Downloading PDF for paper titled: {title}...")
                download_pdf(pdf_url, file_path)
            else:
                # Handle cases where no PDF link is found
                print("No PDF link found for this entry.")


if __name__ == "__main__":
    # Run the main function when the script is executed
    main()
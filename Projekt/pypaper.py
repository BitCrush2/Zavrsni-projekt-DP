import os

def main():
    # Define your search parameters
    query = "ai"  # Replace with your search keywords
    scholar_pages = 2  # Replace with the number of pages you want to scrape
    download_directory = "pdfs"  # Replace with your desired download directory

    # Ensure the download directory exists
    os.makedirs(download_directory, exist_ok=True)

    # Construct the PyPaperBot command
    command = (
        f"python -m PyPaperBot "
        f"--query \"{query}\" "
        f"--scholar-pages {scholar_pages} "
        f"--dwn-dir \"{download_directory}\""
    )

    # Execute the command
    os.system(command)


if __name__ == '__main__':
    main()

import os
import fitz  # PyMuPDF

# Define the folder containing the PDF files
pdf_folder_path = 'pdfs'

# Define the folder to save the extracted text files
output_folder_path = 'txts'

# Create the output folder if it doesn't exist
if not os.path.exists(output_folder_path):
    os.makedirs(output_folder_path)


# Function to extract text from a PDF file
def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        # Open the PDF file
        doc = fitz.open(pdf_path)

        # Iterate through each page
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text += page.get_text()

    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")

    return text


# Iterate through all PDF files in the folder
for filename in os.listdir(pdf_folder_path):
    if filename.endswith('.pdf'):
        pdf_path = os.path.join(pdf_folder_path, filename)
        print(f"Extracting text from: {filename}")

        # Extract text from the PDF
        extracted_text = extract_text_from_pdf(pdf_path)

        # Save the extracted text to a .txt file in the new folder
        output_filename = filename.replace('.pdf', '.txt')
        output_path = os.path.join(output_folder_path, output_filename)

        with open(output_path, 'w', encoding='utf-8') as output_file:
            output_file.write(extracted_text)

        print(f"Text saved to: {output_path}\n")

print("Text extraction completed.")
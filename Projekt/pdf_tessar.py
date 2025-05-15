import os
from pdf2image import convert_from_path
import pytesseract

def main():
    # Set Tesseract path from environment variable or default to a common path
    tesseract_cmd = os.environ.get('TESSERACT_CMD')
    if tesseract_cmd:
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
    else:
        # Optionally check a default path (e.g., common Windows installation)
        default_tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        if os.path.exists(default_tesseract_path):
            pytesseract.pytesseract.tesseract_cmd = default_tesseract_path

    # Set Poppler path from environment variable
    poppler_path = os.environ.get('POPPLER_PATH')

    # Define the input and output directories
    input_folder = 'pdfs'
    output_folder = 'txts'

    # Create the output directory if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Iterate over all PDF files in the input folder
    for pdf_file in os.listdir(input_folder):
        if pdf_file.endswith('.pdf'):
            pdf_path = os.path.join(input_folder, pdf_file)
            text_output_path = os.path.join(output_folder, f"{os.path.splitext(pdf_file)[0]}.txt")

            # Convert PDF to a list of images
            images = convert_from_path(pdf_path, poppler_path=poppler_path)

            # Extract text from each image using pytesseract
            extracted_text = ""
            for i, image in enumerate(images):
                text = pytesseract.image_to_string(image)
                extracted_text += f"--- Page {i + 1} ---\n{text}\n"

            # Save the extracted text to a text file
            with open(text_output_path, 'w', encoding='utf-8') as text_file:
                text_file.write(extracted_text)

            print(f"Extracted text from {pdf_file} and saved to {text_output_path}")

    print("Text extraction completed.")


if __name__ == '__main__':
    main()
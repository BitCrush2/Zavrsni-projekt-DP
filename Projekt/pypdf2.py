import os
from PyPDF2 import PdfReader

# Define input and output directories
input_folder = 'hrcak'
output_folder = 'pypdf2_text'

# Create the output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Iterate through all PDF files in the input folder
for filename in os.listdir(input_folder):
    if filename.lower().endswith('.pdf'):
        pdf_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, f'{os.path.splitext(filename)[0]}.txt')

        try:
            # Open and read the PDF
            with open(pdf_path, 'rb') as pdf_file:
                reader = PdfReader(pdf_file)
                extracted_text = ''

                # Extract text from each page
                for page in reader.pages:
                    extracted_text += page.extract_text() or ''

            # Write the extracted text to a .txt file
            with open(output_path, 'w', encoding='utf-8') as text_file:
                text_file.write(extracted_text)

            print(f'Successfully processed: {filename}')
        except Exception as e:
            print(f'Error processing {filename}: {e}')

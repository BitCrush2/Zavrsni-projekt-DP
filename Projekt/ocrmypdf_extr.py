import os
import ocrmypdf

# Define the input and output directories
input_folder = 'pdfs'
output_folder = 'ocr_text'

# Create the output directory if it doesn't exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Iterate over all PDF files in the input folder
for pdf_file in os.listdir(input_folder):
    if pdf_file.endswith('.pdf'):
        input_pdf_path = os.path.join(input_folder, pdf_file)
        output_pdf_path = os.path.join(output_folder, pdf_file)

        try:
            # Apply OCR to the PDF file
            ocrmypdf.ocr(input_pdf_path, output_pdf_path, deskew=True)
            print(f"Successfully processed: {pdf_file}")
        except Exception as e:
            print(f"Error processing {pdf_file}: {e}")

print("OCR processing completed.")

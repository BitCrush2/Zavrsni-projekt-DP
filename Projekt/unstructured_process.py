import os
from unstructured.partition.pdf import partition_pdf

def main():
    # Define input/output directories
    pdf_dir = "pdfs"
    output_dir = "txts"

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Process PDF files
    for pdf_file in os.listdir(pdf_dir):
        if pdf_file.endswith(".pdf"):
            pdf_path = os.path.join(pdf_dir, pdf_file)

            # Extract elements from PDF using pdfplumber
            elements = partition_pdf(
                pdf_path,
                strategy="hi-res",  # Use "fast" or "hi_res"
                infer_table_structure=True,
                pdf_engine="pdfplumber",  # Use pdfplumber instead of pdf2image
            )

            # Save extracted content to .txt file
            output_path = os.path.join(output_dir, f"{os.path.splitext(pdf_file)[0]}.txt")
            with open(output_path, "w", encoding="utf-8") as f:
                f.write("\n\n".join([str(el) for el in elements]))

    print(f"Processed {len(os.listdir(pdf_dir))} PDFs. Output saved to {output_dir}.")



if __name__ == '__main__':
    main()
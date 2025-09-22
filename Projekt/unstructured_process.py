import os
from unstructured.partition.pdf import partition_pdf


# Create directories if they don't exist
input_folder = "pdfs"
output_folder = "unstruc_txt"

os.makedirs(input_folder, exist_ok=True)
os.makedirs(output_folder, exist_ok=True)


def process_pdfs():
    # Get all PDF files in the input folder
    pdf_files = [f for f in os.listdir(input_folder) if f.lower().endswith('.pdf')]

    if not pdf_files:
        print(f"No PDF files found in the {input_folder} directory.")
        return

    print(f"Found {len(pdf_files)} PDF files to process...")

    for pdf_file in pdf_files:
        try:
            print(f"Processing {pdf_file}...")

            # Construct full file paths
            input_path = os.path.join(input_folder, pdf_file)
            output_path = os.path.join(output_folder, f"{os.path.splitext(pdf_file)[0]}.txt")

            # Extract elements from PDF
            elements = partition_pdf(filename=input_path)

            # Combine all text from elements
            full_text = "\n\n".join([str(el) for el in elements])

            # Write to output file
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(full_text)

            print(f"Successfully processed {pdf_file}")

        except Exception as e:
            print(f"Error processing {pdf_file}: {str(e)}")

def main():
    process_pdfs()


if __name__ == "__main__":
    process_pdfs()
    print("Processing complete!")
import os
import json
import datetime
import re  # For paragraph splitting and regex extraction

def extract_abstract_and_keywords(content):
    """
    Extract abstract and keywords from the content of a .txt file.
    """
    abstract = ""
    keywords = []

    # Extract abstract (assuming it starts with "Abstract:")
    abstract_match = re.search(r'Abstract:\s*(.*?)(?=\n\w+:|$)', content, re.DOTALL)
    if abstract_match:
        abstract = abstract_match.group(1).strip()

    # Extract keywords (assuming they start with "Keywords:")
    keywords_match = re.search(r'Keywords:\s*(.*?)(?=\n\w+:|$)', content, re.DOTALL)
    if keywords_match:
        keywords = [kw.strip() for kw in keywords_match.group(1).split(',')]

    return abstract, keywords

def read_metadata_file(metadata_directory, filename):
    """
    Read the metadata file and extract abstract and keywords.
    """
    metadata_file_path = os.path.join(metadata_directory, filename)
    if os.path.exists(metadata_file_path):
        with open(metadata_file_path, 'r', encoding='utf-8') as metadata_file:
            content = metadata_file.read()
            return extract_abstract_and_keywords(content)
    return "", []

def txt_to_json(directory, metadata_directory):
    """
    Convert .txt files in the specified directory to JSON format.
    """
    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            txt_file_path = os.path.join(directory, filename)

            # Get file metadata
            file_stats = os.stat(txt_file_path)
            file_size = file_stats.st_size  # File size in bytes
            creation_time = datetime.datetime.fromtimestamp(file_stats.st_ctime).isoformat()  # Creation time
            modification_time = datetime.datetime.fromtimestamp(file_stats.st_mtime).isoformat()  # Modification time

            # Read content
            try:
                with open(txt_file_path, 'r', encoding='utf-8') as txt_file:
                    content = txt_file.read()
            except UnicodeDecodeError:
                with open(txt_file_path, 'r', encoding='latin-1') as txt_file:
                    content = txt_file.read()

            # Extract abstract and keywords from the main content
            abstract, keywords = extract_abstract_and_keywords(content)

            # Extract abstract and keywords from the metadata file
            metadata_abstract, metadata_keywords = read_metadata_file(metadata_directory, filename)
            if metadata_abstract:
                abstract = metadata_abstract
            if metadata_keywords:
                keywords = metadata_keywords

            # Analyze the content
            word_count = len(content.split())  # Count words
            line_count = len(content.splitlines())  # Count lines

            # Split into paragraphs
            paragraphs = [
                p.strip()
                for p in re.split(r'\n\s*\n', content)  # Split on 1+ empty lines
                if p.strip()  # Remove empty paragraphs
            ]

            # Modified JSON structure
            json_data = {
                "filename": filename,
                "file_size_bytes": file_size,
                "creation_time": creation_time,
                "modification_time": modification_time,
                "content": content,
                "paragraphs": paragraphs,  # Changed from "content"
                "paragraph_count": len(paragraphs),  # New field
                "metadata": {
                    "word_count": word_count,
                    "line_count": line_count,
                    "avg_paragraph_length": f"{len(content) / len(paragraphs):.1f}" if paragraphs else 0,
                    "abstract": abstract,  # Add abstract
                    "keywords": keywords  # Add keywords
                }
            }
            # Define the output JSON file path
            json_file_path = os.path.join(directory, filename.replace(".txt", ".json"))

            # Write the JSON data to a file
            with open(json_file_path, 'w', encoding='utf-8') as json_file:
                json.dump(json_data, json_file, indent=4, ensure_ascii=False)

            print(f"Transformed {txt_file_path} to {json_file_path}")


def main():
    # Example usage
    directory_path = "txts"
    metadata_directory_path = "metadata"
    txt_to_json(directory_path, metadata_directory_path)


if __name__ == '__main__':
    main()
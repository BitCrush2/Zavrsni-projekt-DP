import os
import json
import datetime
import re  # Added for paragraph splitting


def txt_to_json(directory):
    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            txt_file_path = os.path.join(directory, filename)

            # Get file metadata
            file_stats = os.stat(txt_file_path)
            file_size = file_stats.st_size  # File size in bytes
            creation_time = datetime.datetime.fromtimestamp(file_stats.st_ctime).isoformat()  # Creation time
            modification_time = datetime.datetime.fromtimestamp(file_stats.st_mtime).isoformat()  # Modification time



            # Read content (existing code)
            try:
                with open(txt_file_path, 'r', encoding='utf-8') as txt_file:
                    content = txt_file.read()
            except UnicodeDecodeError:
                with open(txt_file_path, 'r', encoding='latin-1') as txt_file:
                    content = txt_file.read()

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
                "content":content,
                "paragraphs": paragraphs,  # Changed from "content"
                "paragraph_count": len(paragraphs),  # New field
                "metadata": {
                    "word_count": word_count,
                    "line_count": line_count,
                    "avg_paragraph_length": f"{len(content) / len(paragraphs):.1f}" if paragraphs else 0
                }
            }
            # Define the output JSON file path
            json_file_path = os.path.join(directory, filename.replace(".txt", ".json"))

            # Write the JSON data to a file
            with open(json_file_path, 'w', encoding='utf-8') as json_file:
                json.dump(json_data, json_file, indent=4, ensure_ascii=False)

            print(f"Transformed {txt_file_path} to {json_file_path}")


# Example usage
directory_path = "txts"
txt_to_json(directory_path)
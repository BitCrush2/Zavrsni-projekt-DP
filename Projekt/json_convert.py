import os
import json
import datetime


def txt_to_json(directory):
    # Iterate over all files in the directory
    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            # Construct full file path
            txt_file_path = os.path.join(directory, filename)

            # Get file metadata
            file_stats = os.stat(txt_file_path)
            file_size = file_stats.st_size  # File size in bytes
            creation_time = datetime.datetime.fromtimestamp(file_stats.st_ctime).isoformat()  # Creation time
            modification_time = datetime.datetime.fromtimestamp(file_stats.st_mtime).isoformat()  # Modification time

            # Read the content of the txt file with UTF-8 encoding
            try:
                with open(txt_file_path, 'r', encoding='utf-8') as txt_file:
                    content = txt_file.read()
            except UnicodeDecodeError:
                # If UTF-8 fails, try a different encoding (e.g., 'latin-1')
                with open(txt_file_path, 'r', encoding='latin-1') as txt_file:
                    content = txt_file.read()

            # Analyze the content
            word_count = len(content.split())  # Count words
            line_count = len(content.splitlines())  # Count lines

            # Transform the content and metadata into a JSON object
            json_data = {
                "filename": filename,
                "file_size_bytes": file_size,
                "creation_time": creation_time,
                "modification_time": modification_time,
                "content": content,
                "metadata": {
                    "word_count": word_count,
                    "line_count": line_count
                }
            }

            # Define the output JSON file path
            json_file_path = os.path.join(directory, filename.replace(".txt", ".json"))

            # Write the JSON data to a file
            with open(json_file_path, 'w', encoding='utf-8') as json_file:
                json.dump(json_data, json_file, indent=4, ensure_ascii=False)

            print(f"Transformed {txt_file_path} to {json_file_path}")


# Example usage
directory_path = "pdf2image_text"
txt_to_json(directory_path)
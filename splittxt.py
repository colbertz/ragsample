import sys
from langchain.text_splitter import RecursiveCharacterTextSplitter
import hashlib
import json
import os

def main():
    if len(sys.argv) != 2:
        print("Usage: python splittxt.py <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]

    try:
        with open(input_file, 'r', encoding='utf-8') as file:
            text = file.read()
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.")
        sys.exit(1)

    # Calculate SHA1 hash for the document ID
    sha1 = hashlib.sha1(text.encode('utf-8')).hexdigest()
    docid = sha1

    # Initialize the RecursiveCharacterTextSplitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,  # Adjust chunk size as needed
        separators=["\n", "!", "?", ";", "。", "；", "！", "？"],  # Specify custom split characters
    )

    # Split the text
    chunks = text_splitter.split_text(text)

    # Trim leading separator characters from each chunk
    trimmed_chunks = [chunk.lstrip("\n!?;。；！？") for chunk in chunks]

    # Prepare the JSON output as a list
    output = [
        {
            "chunkid": docid + '_' + str(i + 1),
            "content": chunk
        }
        for i, chunk in enumerate(trimmed_chunks)
    ]

    # Determine output file name
    base_name = os.path.basename(input_file).split('.')[0]  # Extract base name before any dots
    output_file = f"{base_name}.chunks.json"

    # Write the JSON output to the file
    with open(output_file, 'w', encoding='utf-8') as outfile:
        json.dump(output, outfile, ensure_ascii=False, indent=2)

    print(f"Chunks written to {output_file}")

if __name__ == "__main__":
    main()
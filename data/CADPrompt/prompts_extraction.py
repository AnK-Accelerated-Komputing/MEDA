import os
import sys
from pathlib import Path

def extract_text_contents(root_dir, output_file, target_filename):
    """
    Traverse a directory structure, extract contents from specific text files,
    and write them to an output file along with their folder names.
    
    Args:
        root_dir (str): Path to the root directory to start traversal
        output_file (str): Path to the output file where results will be saved
        target_filename (str): Name of the target text files to extract content from
    """
    # Convert to absolute path and check if root directory exists
    root_dir = os.path.abspath(root_dir)
    if not os.path.isdir(root_dir):
        print(f"Error: The directory '{root_dir}' does not exist.")
        sys.exit(1)
    
    print(f"Scanning directory: {root_dir}")
    print(f"Looking for files named: {target_filename}")
    print(f"Results will be saved to: {output_file}")
    
    # Keep track of statistics
    folders_processed = 0
    files_found = 0
    
    with open(output_file, 'w', encoding='utf-8') as out_f:
        # Walk through directory structure
        for dirpath, dirnames, filenames in os.walk(root_dir):
            # Skip the root directory itself
            if dirpath == root_dir:
                continue
                
            # Check if the target file exists in this directory
            target_file_path = os.path.join(dirpath, target_filename)
            if os.path.isfile(target_file_path):
                folder_name = os.path.basename(dirpath)
                
                try:
                    # Read the content of the target file
                    with open(target_file_path, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                    
                    # Write to the output file in the requested format
                    out_f.write(f"{folder_name}:{content}\n")
                    
                    files_found += 1
                    print(f"Processed: {folder_name}")
                    
                except Exception as e:
                    print(f"Error reading file in folder '{folder_name}': {e}")
            
            folders_processed += 1
    
    print(f"\nSummary:")
    print(f"Folders processed: {folders_processed}")
    print(f"Files found and processed: {files_found}")
    print(f"Results saved to: {output_file}")

if __name__ == "__main__":
    # Default values
    target_filename = "Natural_Language_Descriptions_Prompt_with_specific_measurements.txt"
    
    # Get root directory from command line or use current directory
    if len(sys.argv) > 1:
        root_directory = sys.argv[1]
    else:
        root_directory = os.getcwd()
        print("No directory specified, using current directory.")
    
    # Get output file path from command line or use default
    if len(sys.argv) > 2:
        output_file_path = sys.argv[2]
    else:
        output_file_path = "combined_folder_contents.txt"
        print(f"No output file specified, using '{output_file_path}'.")
    
    # Extract the contents
    extract_text_contents(root_directory, output_file_path, target_filename)
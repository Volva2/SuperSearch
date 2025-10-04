import subprocess
import json

import subprocess
import json
import os # Added for path handling

def search_content(term: str, folder=None):
    """
    Searches for a term in a given folder using ripgrep (rg) and returns matches.

    Args:
        term (str): The search term (can be a regex).
        folder (str, optional): The folder to search in. Defaults to the user's home directory.

    Returns:
        list: A list of dictionaries, each representing a match.
              Returns an empty list if ripgrep is not found or an error occurs.
    """
    # Fix #5: Use a safer default directory like the user's home folder.
    if folder is None:
        folder = os.path.expanduser("~")

    command = ["rg", "--json", "-F", "-w", term, folder]

    try:
        # Fix #3: Add check=True to automatically raise an error if rg fails.
        result = subprocess.run(
            command, capture_output=True, text=True, check=True, encoding='utf-8'
        )
    except FileNotFoundError:
        # Fix #2: Handle the case where ripgrep (rg) is not installed or not in the PATH.
        print("Error: 'rg' (ripgrep) command not found.")
        print("Please install ripgrep and ensure it is in your system's PATH.")
        return []
    except subprocess.CalledProcessError as e:
        # Fix #3: Catch errors from ripgrep itself (e.g., directory not found, invalid regex).
        print(f"Error executing ripgrep: {e}")
        print(f"ripgrep stderr:\n{e.stderr}")
        return []

    matches = []
    for line in result.stdout.splitlines():
        try:
            # Fix #4: Add a try/except block to gracefully handle non-JSON lines or unexpected formats.
            obj = json.loads(line)
            if obj.get("type") == "match":
                # Using .get() for nested values adds robustness against format changes.
                data = obj.get("data", {})
                path_text = data.get("path", {}).get("text")
                line_num = data.get("line_number")
                lines_text = data.get("lines", {}).get("text", "").strip()

                if all([path_text, line_num, lines_text]): # Ensure all data was found
                    matches.append({
                        "file": path_text,
                        "line": line_num,
                        "text": lines_text
                    })
        except (json.JSONDecodeError, KeyError) as e:
            # This line might not be a match object, or its format is unexpected.
            # print(f"Skipping malformed line: {line} | Error: {e}")
            pass # Silently skip non-match lines (like 'begin', 'end', 'summary')

    return matches

if __name__ == '__main__':
    print("Searching for the term 'import' in the current directory...")
    found_matches = search_content("hello", ".")
    print(found_matches)
    if found_matches:
        for match in found_matches[:5]:
            print(f"- File: {match['file']}, Line: {match['line']}\n  Text: {match['text']}\n")
    else:
        print("No matches found or an error occurred.")
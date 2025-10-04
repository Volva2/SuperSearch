import subprocess
import json
import os

def search_content(term: str, folder=None):
    if folder is None:
        folder = os.path.expanduser("~")

    command = ["rg", "--json", "-F", "-w", term, folder]

    try:
        result = subprocess.run(
            command, capture_output=True, text=True, check=True, encoding='utf-8'
        )
    except FileNotFoundError:
        print("Error: 'rg' (ripgrep) command not found.")
        print("Please install ripgrep and ensure it is in your system's PATH.")
        return []
    except subprocess.CalledProcessError as e:
        print(f"Error executing ripgrep: {e}")
        print(f"ripgrep stderr:\n{e.stderr}")
        return []

    matches = []
    for line in result.stdout.splitlines():
        try:
            obj = json.loads(line)
            if obj.get("type") == "match":
                data = obj.get("data", {})
                path_text = data.get("path", {}).get("text")
                line_num = data.get("line_number")
                lines_text = data.get("lines", {}).get("text", "").strip()

                if all([path_text, line_num, lines_text]):
                    matches.append({
                        "file": path_text,
                        "line": line_num,
                        "text": lines_text
                    })
        except (json.JSONDecodeError, KeyError) as e:
            pass

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
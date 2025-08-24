import subprocess
import json

def search_content(term: str, folder="C:"):
    result = subprocess.run(
        ["rg", "--json", term, folder], capture_output=True, text=True
    )
    matches = []
    for line in result.stdout.splitlines():
        obj = json.loads(line)
        if obj.get("type") == "match":
            matches.append({
                "file": obj["data"]["path"]["text"],
                "line": obj["data"]["line_number"],
                "text": obj["data"]["lines"]["text"].strip()
            })
    return matches
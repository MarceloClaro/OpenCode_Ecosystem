import requests
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Verify the replacement
r = requests.get("https://api.crossref.org/works/10.51473/rcmos.v2i2.25")
data = r.json()["message"]
print("Title:", data.get("title", [""])[0])
print("Authors:", ", ".join(f"{a.get('given', '')} {a.get('family', '')}" for a in data.get("author", [])))
print("Journal:", data.get("container-title", [""])[0])
year_parts = data.get("published-print", {}).get("date-parts", [[]])[0]
print("Year:", year_parts[0] if year_parts else "N/A")
print("DOI:", data.get("DOI"))
print("URL:", f"https://doi.org/{data.get('DOI')}")

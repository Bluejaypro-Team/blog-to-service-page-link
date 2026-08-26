import os
import re
import json

blogs_dir = r"C:\Users\BlueJayPro\.gemini\antigravity-ide\scratch\proglassgv\blogs"
summary_json = os.path.join(blogs_dir, "scrape_summary.json")

with open(summary_json, "r", encoding="utf-8") as f:
    items = json.load(f)

index_md = """# Pro Glass & Mirror (`proglassgv.com`) — Master Blog Content Index

**Total Blog Posts Scraped:** 19  
**Domain:** `https://proglassgv.com/`  
**Storage Directory:** `C:\\Users\\BlueJayPro\\.gemini\\antigravity-ide\\scratch\\proglassgv\\blogs\\`  

---

## Blog Post Catalog & Headings Summary

"""

for idx, item in enumerate(items, 1):
    slug = item.get("slug")
    url = item.get("url")
    title = item.get("title", slug)
    filepath = item.get("file")
    
    headings = []
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as bf:
            content = bf.read()
            # Extract H2 headings
            h2_matches = re.findall(r'^##\s+(.*)$', content, re.MULTILINE)
            headings = [h.strip() for h in h2_matches if h.strip() and not h.startswith('#')]
    
    index_md += f"### {idx}. {title}\n"
    index_md += f"- **URL:** `{url}`\n"
    index_md += f"- **File Path:** [`{slug}.md`](file:///{filepath.replace('\\', '/')})\n"
    if headings:
        index_md += f"- **Key Sections / H2 Headings:**\n"
        for h in headings[:8]: # top 8 H2s
            index_md += f"  - {h}\n"
    index_md += "\n---\n\n"

index_file = r"C:\Users\BlueJayPro\.gemini\antigravity-ide\scratch\proglassgv\proglass_blogs_master_index.md"
with open(index_file, "w", encoding="utf-8") as f:
    f.write(index_md)

artifact_file = r"C:\Users\BlueJayPro\.gemini\antigravity-ide\brain\1eae34b4-6fc5-4524-84e4-a27fc6766f17\proglass_blogs_master_index.md"
with open(artifact_file, "w", encoding="utf-8") as f:
    f.write(index_md)

print("Generated master blog index successfully.")

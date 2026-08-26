import os
import re
import urllib.request
import json
from html.parser import HTMLParser

urls = [
    "https://proglassgv.com/storefront-glazing-vs-curtain-wall/",
    "https://proglassgv.com/storefront-glass-replacement-signs/",
    "https://proglassgv.com/framed-vs-frameless-office-glass/",
    "https://proglassgv.com/tubular-vs-traditional-skylights/",
    "https://proglassgv.com/key-benefits-demountable-office-wall-systems/",
    "https://proglassgv.com/shower-enclosure-maintenance-tips/",
    "https://proglassgv.com/low-iron-glass-shower-enclosure-benefits/",
    "https://proglassgv.com/frameless-vs-framed-shower-doors/",
    "https://proglassgv.com/retrofit-vs-full-frame-window-replacement/",
    "https://proglassgv.com/retrofit-window-maintenance-tips/",
    "https://proglassgv.com/flush-fin-windows-benefits-stucco-homes/",
    "https://proglassgv.com/signs-you-need-window-replacement/",
    "https://proglassgv.com/curtain-wall-vs-storefront/",
    "https://proglassgv.com/unitized-curtain-wall-vs-stick-built/",
    "https://proglassgv.com/tempered-vs-laminated-glass/",
    "https://proglassgv.com/deck-mounted-skylight-vs-curb/",
    "https://proglassgv.com/frameless-vs-post-railing-systems/",
    "https://proglassgv.com/skylight-maintenance-checklist/",
    "https://proglassgv.com/benefits-of-natural-lighting/"
]

output_dir = r"C:\Users\BlueJayPro\.gemini\antigravity-ide\scratch\proglassgv\blogs"
os.makedirs(output_dir, exist_ok=True)

class HTMLToMD(HTMLParser):
    def __init__(self):
        super().__init__()
        self.result = []
        self.in_title = False
        self.title = ""
        self.in_content = False
        self.current_tag = None
        self.in_heading = False
        self.heading_level = 1
        self.in_link = False
        self.link_href = ""
        self.link_text = ""

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == 'title':
            self.in_title = True
        if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            self.in_heading = True
            self.heading_level = int(tag[1])
            self.result.append(f"\n\n{'#' * self.heading_level} ")
        elif tag == 'p':
            self.result.append("\n\n")
        elif tag == 'li':
            self.result.append("\n- ")
        elif tag == 'a':
            self.in_link = True
            self.link_href = attrs_dict.get('href', '')
            self.link_text = ""

    def handle_endtag(self, tag):
        if tag == 'title':
            self.in_title = False
        elif tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            self.in_heading = False
        elif tag == 'a':
            self.in_link = False
            if self.link_href:
                self.result.append(f"[{self.link_text.strip()}]({self.link_href})")
            else:
                self.result.append(self.link_text)

    def handle_data(self, data):
        if self.in_title:
            self.title += data
        elif self.in_link:
            self.link_text += data
        else:
            self.result.append(data)

def scrape_url(url):
    slug = url.strip('/').split('/')[-1]
    print(f"Scraping {slug}...")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            
            # Simple content area extraction if possible (e.g. entry-content, article, or main)
            # Find title
            title_match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
            title = title_match.group(1).strip() if title_match else slug
            
            # Extract main content body
            content_html = html
            # Try to narrow down to post content if standard WordPress / Elementor tags exist
            for pattern in [r'<div class="[^"]*entry-content[^"]*">(.*?)</div>\s*<!-- \.entry-content',
                            r'<article[^>]*>(.*?)</article>',
                            r'<main[^>]*>(.*?)</main>',
                            r'<div class="[^"]*elementor-widget-container[^"]*">(.*?)</div>']:
                match = re.search(pattern, html, re.DOTALL | re.IGNORECASE)
                if match:
                    # Don't restrict too heavily if match is tiny, but article/main is good
                    if len(match.group(1)) > 500:
                        content_html = match.group(1)
                        break

            # Convert HTML to clean text/markdown using regex cleanings
            # Strip scripts, styles, nav, header, footer
            clean = re.sub(r'<(script|style|header|footer|nav|aside)[^>]*>.*?</\1>', '', html, flags=re.DOTALL | re.IGNORECASE)
            
            # Extract H1..H6, P, LI, A
            parser = HTMLToMD()
            parser.feed(clean)
            text_content = "".join(parser.result)
            
            # Clean up whitespace
            text_content = re.sub(r'\n{3,}', '\n\n', text_content)
            
            md_file = os.path.join(output_dir, f"{slug}.md")
            with open(md_file, "w", encoding="utf-8") as f:
                f.write(f"# {title}\n\n**URL:** {url}\n\n---\n\n{text_content.strip()}")
            
            return {
                "slug": slug,
                "url": url,
                "title": title,
                "file": md_file,
                "status": "success"
            }
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return {
            "slug": slug,
            "url": url,
            "error": str(e),
            "status": "failed"
        }

if __name__ == "__main__":
    results = []
    for u in urls:
        res = scrape_url(u)
        results.append(res)
    
    summary_file = os.path.join(output_dir, "scrape_summary.json")
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print("Done scraping all posts.")

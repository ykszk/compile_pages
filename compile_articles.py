import os
import time
import argparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from PyPDF2 import PdfMerger
import base64

def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")  # use headless mode
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument('--kiosk-printing')
    return webdriver.Chrome(options=chrome_options)

def print_to_pdf(driver, url, filename, sleep_time):
    driver.get(url)
    time.sleep(sleep_time)  # Let content fully load
    result = driver.execute_cdp_cmd("Page.printToPDF", {
        "printBackground": True,
        "format": "A4"
    })
    with open(filename, "wb") as f:
        f.write(base64.b64decode(result['data']))

def extract_title(driver):
    try:
        return driver.title.strip()
    except:
        return "Untitled"

def main(urls, args):
    output_pdf = args.output
    output_dir = "pdfs"
    os.makedirs(output_dir, exist_ok=True)

    driver = get_driver()
    pdf_paths = []
    titles = []

    for i, url in enumerate(urls):
        pdf_file = os.path.join(output_dir, f"article_{i+1}.pdf")
        print(f"Processing: {url}")
        print_to_pdf(driver, url, pdf_file, args.sleep)
        title = extract_title(driver)
        titles.append(title or f"Article {i+1}")
        pdf_paths.append(pdf_file)

    driver.quit()

    # Merge PDFs and add bookmarks
    merger = PdfMerger()
    for pdf_path, title in zip(pdf_paths, titles):
        merger.append(pdf_path, outline_item=title)

    merger.write(output_pdf)
    merger.close()

    print(f"\nCompiled PDF saved to: {output_pdf}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compile blog articles into a single PDF with bookmarks.")
    parser.add_argument("urls", nargs="*", help="List of blog article URLs")
    parser.add_argument("--text", type=str, help="Text file containing URLs (one per line)")
    parser.add_argument("-o", "--output", default="compiled_articles.pdf", help="Output PDF filename (default: %(default)s.pdf)")
    parser.add_argument("--sleep", type=int, default=1, help="Sleep time in seconds to wait for content to load (default: %(default)s)")
    args = parser.parse_args()

    urls = args.urls
    if args.text:
        with open(args.text, "r") as f:
            urls = [line.strip() for line in f.readlines()]

    main(urls, args)

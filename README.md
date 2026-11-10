# Automated Web Scraping & Data Extraction Pipelines

Production-ready Python web scraping pipelines built to extract, clean, and aggregate structured business datasets from both static HTML and dynamic JavaScript-rendered websites.

## Key Capabilities & Engineering Highlights

- **Static & Deep Scraping (`static_book_scraper.py`)**:
  - Handles automated pagination (`li.next > a`) and relative URL resolution via `urllib.parse.urljoin`.
  - Performs multi-level (deep) scraping into individual product pages for category and inventory extraction.
  - Enforces UTF-8 encoding and Regex-based data sanitization (`re.sub`) to clean dirty currency/stock strings.
  - Implements request timeouts, HTTP error handling, and polite rate-limiting.
- **Dynamic JavaScript Scraping (`dynamic_quote_scraper.py`)**:
  - Uses **Playwright** with headless Chromium to scrape client-side rendered (JS) web applications.
  - Implements event-driven waiting (`wait_for_selector`) instead of fixed sleeps for stability and speed.
- **Automated BI Reporting**:
  - Transforms raw extracted records using **Pandas** into multi-sheet Excel workbooks (`Raw_Data` + aggregated `Summary` analytics).

## Tech Stack

- **Language**: Python 3
- **Scraping**: `requests`, `BeautifulSoup4`, `Playwright`
- **Data Processing & Export**: `pandas`, `openpyxl`, `re`

## Sample Output Preview

| Title | Category | Price_GBP | Rating | Stock_Qty |
| :--- | :--- | :---: | :---: | :---: |
| A Light in the Attic | Poetry | 51.77 | 3 | 22 |
| Sharp Objects | Mystery | 47.82 | 4 | 20 |
| Sapiens: A Brief History of Humankind | History | 54.23 | 5 | 20 |

## How to Run Locally

```bash
# 1. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt
playwright install chromium

# 3. Run the scrapers
python static_book_scraper.py
python dynamic_quote_scraper.py
```
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from urllib.parse import urljoin

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

RATING_MAP = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}

def get_soup(url):
    """ฟังก์ชันช่วยยิง Request แบบปลอดภัย มี timeout และเช็ก error"""
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()  # ถ้าไม่ใช่ 200 OK ให้โยน Error ทันที
        response.encoding = "utf-8"
        return BeautifulSoup(response.text, "html.parser")
    except requests.RequestException as e:
        print(f"⚠️ โหลดหน้านี้ไม่สำเร็จ ({url}): {e}")
        return None

def scrape_book_details(book_url):
    """Deep Scraping: เข้าไปดึง Category และจำนวนสต็อกตัวเลขจริงจากหน้าสินค้าย่อย"""
    soup = get_soup(book_url)
    if not soup:
        return "Unknown", 0

    # 1. ดึง Category จากแถบ Breadcrumb (Home > Books > Category > Title)
    breadcrumb_links = soup.select("ul.breadcrumb li a")
    # ตำแหน่งที่ 2 (index 2) คือชื่อหมวดหมู่
    category = breadcrumb_links[2].text.strip() if len(breadcrumb_links) > 2 else "Unknown"

    # 2. ดึงจำนวนสต็อกจริง เช่น "In stock (22 available)" -> 22
    stock_el = soup.find("p", class_="instock availability")
    stock_qty = 0
    if stock_el:
        match = re.search(r"\d+", stock_el.text)
        if match:
            stock_qty = int(match.group())

    return category, stock_qty

def run_scraper(max_pages=2):
    # ตั้ง max_pages=None ถ้าอยากให้ดึงจนหมดทั้งเว็บ (1,000 เล่ม จะใช้เวลาหลายนาที)
    current_url = "http://books.toscrape.com/catalogue/page-1.html"
    all_books = []
    page_count = 0

    print("🚀 เริ่มทำงาน Production Scraper (V2)...")

    while current_url:
        page_count += 1
        if max_pages and page_count > max_pages:
            print(f"🛑 หยุดตามโควตาทดสอบ ({max_pages} หน้า)")
            break

        print(f"\n📄 กำลังสแกนหน้า {page_count}: {current_url}")
        soup = get_soup(current_url)
        if not soup:
            break

        book_cards = soup.find_all("article", class_="product_pod")

        for idx, book in enumerate(book_cards, start=1):
            title = book.h3.a["title"]
            
            # ต่อ URL หน้าสินค้าให้สมบูรณ์ด้วย urljoin
            relative_link = book.h3.a["href"]
            book_url = urljoin(current_url, relative_link)

            raw_price = book.find("p", class_="price_color").text
            clean_price = float(re.sub(r"[^\d.]", "", raw_price))

            star_class = book.find("p", class_="star-rating")["class"]
            rating_num = RATING_MAP.get(star_class[1] if len(star_class) > 1 else "", 0)

            # เข้าไปดึงข้อมูลเชิงลึกจากหน้าสินค้าย่อย
            print(f"   [{idx}/{len(book_cards)}] เจาะข้อมูล: {title[:35]}...")
            category, stock_qty = scrape_book_details(book_url)

            all_books.append({
                "Title": title,
                "Category": category,
                "Price_GBP": clean_price,
                "Rating": rating_num,
                "Stock_Qty": stock_qty,
                "Product_URL": book_url
            })
            time.sleep(0.2)  # หน่วงเวลานิดหน่อยกันโดนแบน IP

        # Auto-Pagination: หาปุ่ม Next เพื่อไปหน้าถัดไป
        next_btn = soup.select_one("li.next > a")
        if next_btn:
            current_url = urljoin(current_url, next_btn["href"])
        else:
            print("🏁 ถึงหน้าสุดท้ายของเว็บแล้ว!")
            current_url = None

    if not all_books:
        print("❌ ไม่มีข้อมูลถูกดึงออกมา")
        return

    # สร้าง DataFrame หลัก
    df = pd.DataFrame(all_books)

    # สร้างตารางสรุปข้อมูลแยกตาม Category (Data Analytics Value!)
    summary_df = df.groupby("Category", as_index=False).agg(
        Total_Books=("Title", "count"),
        Avg_Price_GBP=("Price_GBP", "mean"),
        Max_Price_GBP=("Price_GBP", "max"),
        Total_Stock=("Stock_Qty", "sum")
    ).sort_values(by="Total_Books", ascending=False)
    summary_df["Avg_Price_GBP"] = summary_df["Avg_Price_GBP"].round(2)

    # Export ลงไฟล์ Excel แบบ 2 Sheets
    output_file = "books_report_v2.xlsx"
    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Raw_Data", index=False)
        summary_df.to_excel(writer, sheet_name="Category_Summary", index=False)

    print(f"\n✅ เสร็จสมบูรณ์! ดึงข้อมูลทั้งหมด {len(df)} รายการลงไฟล์ '{output_file}' (2 Sheets) เรียบร้อย")

if __name__ == "__main__":
    run_scraper(max_pages=2)
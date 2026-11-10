from playwright.sync_api import sync_playwright
import pandas as pd

def run_dynamic_scraper(max_pages=3):
    all_quotes = []

    with sync_playwright() as p:
        # headless=False: สั่งให้เปิดหน้าต่าง Chrome ขึ้นมาให้เราดูสดๆ
        # slow_mo=300: หน่วงให้บอทขยับช้าลง 0.3 วินาที จะได้มองตามทัน
        browser = p.chromium.launch(headless=False, slow_mo=300)
        page = browser.new_page()

        url = "https://quotes.toscrape.com/js/"
        print(f"🌐 กำลังเปิดเบราว์เซอร์ไปยัง: {url}")
        page.goto(url)

        for current_page in range(1, max_pages + 1):
            print(f"📄 กำลังดึงข้อมูลหน้าที่ {current_page}...")

            # หัวใจสำคัญของ Playwright: รอจนกว่า JavaScript จะสร้างกล่อง Quote เสร็จ
            page.wait_for_selector("div.quote")

            # ดึงกล่อง Quote ทั้งหมดในหน้านี้
            quote_cards = page.locator("div.quote").all()

            for card in quote_cards:
                text = card.locator("span.text").inner_text().strip()
                author = card.locator("small.author").inner_text().strip()
                # เพราะ 1 Quote มีได้หลาย Tag จึงใช้ .all_inner_texts() แล้วคั่นด้วยลูกน้ำ
                tags = card.locator("div.tags a.tag").all_inner_texts()

                all_quotes.append({
                    "Quote": text,
                    "Author": author,
                    "Tags": ", ".join(tags),
                    "Page": current_page
                })

            # หาปุ่ม Next แล้วคลิกเปลี่ยนหน้าเหมือนคนกดเองจริงๆ
            next_btn = page.locator("li.next a")
            if next_btn.count() > 0 and current_page < max_pages:
                next_btn.click()
            else:
                break

        browser.close()

    # แปลงเป็น DataFrame และทำตารางสรุปให้ลูกค้า
    df = pd.DataFrame(all_quotes)
    author_summary = df.groupby("Author", as_index=False).agg(
        Quote_Count=("Quote", "count")
    ).sort_values(by="Quote_Count", ascending=False)

    output_file = "quotes_dynamic.xlsx"
    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Quotes_Data", index=False)
        author_summary.to_excel(writer, sheet_name="Author_Summary", index=False)

    print(f"\n✅ เสร็จสิ้น! ดึงข้อมูลด้วย Playwright ได้ทั้งหมด {len(df)} รายการ -> '{output_file}'")

if __name__ == "__main__":
    run_dynamic_scraper(max_pages=3)
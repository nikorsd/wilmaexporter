import os
import re
import time
from datetime import datetime
from playwright.sync_api import sync_playwright

def main():
    print("WELCOME TO WILMA EXPORTER! by nikorsd")
    print("----------------------------------------------")

    wilmaurl = input ("Enter your Wilma URL (example. https://ouka.inschool.fi/): ")

    delay = input("Enter delay between messages in seconds (e.g. 1.5): ")
    try:
        delay = float(delay)
    except ValueError:
        print("Invalid input, using default delay of 1 second.")
        delay = 1.0

    pages = input("Input the number of pages you want to scrape: ")
    try:
        pages = float(pages)
    except ValueError:
        print("Invalid input. Enter a number\nScript will now exit")
        return
    
    unknownname = input("Enter your name. This will be used in filenames. (Input default for default value): ")
    if unknownname == "default":
        print("Acknowledged. Using Unknown")

    base_url = "https://ouka.inschool.fi/!02210673/messages"
    output_dir = "messages"
    os.makedirs(output_dir, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        try:
            page.goto(wilmaurl)
        except:
            print(f"Error trying to go to {wilmaurl}. Check spelling. Has to contain full URL.\nScript will now exit.")

        input("Log into Wilma in the new browser window and press enter here once complete...")

        page_number = 1

        while page_number <= pages:
            message_page_url = f"{base_url}/?page={page_number}"
            print(f"Scraping page {page_number} → {message_page_url}")
            page.goto(message_page_url)
            page.wait_for_load_state("networkidle")

            # Select all message links
            links = page.query_selector_all("a.no-underline-link")
            hrefs = [l.get_attribute("href") for l in links if l.get_attribute("href")]

            if not hrefs:
                print("No more messages found. Exiting.")
                break

            print(f"Found {len(hrefs)} messages.")

            for href in hrefs:
                full_url = "https://ouka.inschool.fi" + href + "?printable"
                page.goto(full_url)
                page.wait_for_load_state("networkidle")

                try:
                    # Get full page content for regex extraction
                    page_content = page.content()

                    # Extract teacher name and ID from printable HTML
                    match = re.search(r"Lähettäjä:\s*</th>\s*<td>([^<]+)\(([^)]+)\)", page_content)
                    if match:
                        teacherid = match.group(2).strip()
                    else:
                        teacherid = unknownname

                    # Extract sent time from printable HTML
                    sent_time_match = re.search(
                        r"Lähetetty:\s*</th>\s*<td>(\d{1,2})\.(\d{1,2})\.(\d{4}) klo (\d{1,2}):(\d{2})",
                        page_content
                    )
                    if sent_time_match:
                        day, month, year, hour, minute = map(int, sent_time_match.groups())
                        dt = datetime(year, month, day, hour, minute)
                    else:
                        dt = datetime.now()

                    # Format and save file
                    filename = dt.strftime(f"%Y-%m-%d-%H.%M-{teacherid}.html")
                    path = os.path.join(output_dir, filename)

                    with open(path, "w", encoding="utf-8") as f:
                        f.write(page_content)

                    print(f"Saved HTML: {filename}")

                except Exception as e:
                    print(f"Failed on {full_url}: {e}")

                time.sleep(delay)

            page_number += 1

        browser.close()

if __name__ == "__main__":
    main()

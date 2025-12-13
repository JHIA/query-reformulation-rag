from firecrawl import Firecrawl
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import os
import time
from bs4 import BeautifulSoup
import re
import json
from config import API_FIRECRAWL


API_KEY = os.getenv("FIRECRAWL_API_KEY", API_FIRECRAWL)
fc = Firecrawl(api_key=API_KEY)

def extract_article_links(list_url):
    print("Fetching list page:", list_url)
    doc = fc.scrape(list_url, formats=["html"])
    html = doc.html
    soup = BeautifulSoup(html, "html.parser")
    links = []
    
    for a in soup.select("a[href]"):
        href = a.get("href")
        text = a.get_text(strip=True)
        if not href or not text:
            continue
        if "/klinik/a/" in href:
            if href.startswith("/"):
                href = "https://www.hukumonline.com" + href
            links.append({"title": text, "link": href})
    
    seen = set()
    unique_links = []
    for item in links:
        if item["link"] not in seen:
            seen.add(item["link"])
            unique_links.append(item)
    
    print(f"Found {len(unique_links)} unique links on {list_url}")
    return unique_links

def extract_publish_date(soup):
    """Extract publish date from the article page"""
    # Coba beberapa selector untuk tanggal
    
    # 1. Cari di metadata
    date_meta = soup.find("meta", property="article:published_time")
    if date_meta and date_meta.get("content"):
        return date_meta.get("content")
    
    # 2. Cari di structured data (JSON-LD)
    script_tags = soup.find_all("script", type="application/ld+json")
    for script in script_tags:
        try:
            data = json.loads(script.string)
            if isinstance(data, dict):
                if "datePublished" in data:
                    return data["datePublished"]
                if "publishedTime" in data:
                    return data["publishedTime"]
        except:
            pass
    
    # 3. Cari di elemen dengan class/id yang mengandung tanggal
    date_elem = soup.find("time")
    if date_elem:
        return date_elem.get("datetime") or date_elem.get_text(strip=True)
    
    # 4. Cari pattern tanggal dalam teks (format: DD MMM, YYYY)
    date_pattern = re.compile(r'\d{1,2}\s+(?:Jan|Feb|Mar|Apr|Mei|Jun|Jul|Agu|Sep|Okt|Nov|Des)[a-z]*,?\s+\d{4}')
    text = soup.get_text()
    match = date_pattern.search(text)
    if match:
        return match.group(0)
    
    return None

def extract_article_content(html):
    """Extract clean article content from HTML"""
    soup = BeautifulSoup(html, "html.parser")
    
    # Cari wrapper utama yang berisi konten artikel
    main_wrapper = soup.select_one("div.css-103zlhi.elbhtsw0")
    
    if main_wrapper:
        # Hapus elemen yang tidak diinginkan HANYA di dalam wrapper ini
        unwanted_selectors = [
            "article.css-1eyd3st.ejhsnq53",  # KLINIK TERKAIT section
            "div.css-ukcqzp",  # Iklan kursus online
            "div.css-uk4b7z",  # Iklan in-article
            "div.adunitContainer",  # Container iklan
            ".swiper",  # Carousel
            "iframe",  # Iframes
        ]
        
        for selector in unwanted_selectors:
            for elem in main_wrapper.select(selector):
                elem.decompose()
        
        # Cari div yang berisi konten artikel (css-15rxf41)
        content_div = main_wrapper.select_one("div.css-15rxf41.e1vjmfpm0")
        
        if content_div:
            # Ambil semua teks dari content_div dengan separator spasi
            text = content_div.get_text(separator=" ", strip=True)
            
            # Bersihkan teks yang tidak diinginkan
            text = re.sub(r'KLINIK TERKAIT.*?(?=\s[A-Z]|\s\s|$)', '', text, flags=re.DOTALL)
            text = re.sub(r'Belajar Hukum Secara Online.*?Lihat Semua Kelas\s*', '', text, flags=re.DOTALL)
            text = re.sub(r'Navigate (left|right)\s*', '', text, flags=re.IGNORECASE)
            
            # Bersihkan whitespace berlebih (multiple spaces menjadi 1 space)
            text = re.sub(r'\s+', ' ', text)
            
            return text.strip()
    
    # Fallback 1: Cari langsung content wrapper
    wrapper = soup.select_one("div.css-15rxf41.e1vjmfpm0")
    if wrapper:
        # Hapus elemen tidak diinginkan
        for selector in ["article.css-1eyd3st", "div.css-ukcqzp", "div.css-uk4b7z"]:
            for elem in wrapper.select(selector):
                elem.decompose()
        
        text = wrapper.get_text(separator=" ", strip=True)
        text = re.sub(r'KLINIK TERKAIT.*?(?=\s[A-Z]|\s\s|$)', '', text, flags=re.DOTALL)
        text = re.sub(r'Belajar Hukum Secara Online.*?Lihat Semua Kelas\s*', '', text, flags=re.DOTALL)
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    # Fallback 2: Ambil semua teks
    text = soup.get_text(separator=" ", strip=True)
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def scrape_tags_with_selenium(url):
    """Extract tags from article using Selenium"""
    try:
        options = Options()
        # Uncomment line dibawah jika ingin headless mode
        # options.add_argument('--headless')
        
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get(url)
        
        # Tunggu halaman sepenuhnya termuat
        time.sleep(2)
        
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        
        tags_div = soup.select_one('div.css-17qwrqj.e12pag3i0')
        if tags_div:
            tag_links = tags_div.select('a.__tag_click')
            tags_list = [link.get_text(strip=True) for link in tag_links]
            driver.quit()
            return tags_list
        else:
            driver.quit()
            return []
        
    except Exception as e:
        print(f"Error scraping tags: {e}")
        return []

def scrape_full_article(article, theme):
    """Scrape full article with all metadata including tags"""
    url = article["link"]
    print("Scraping article:", url)
    
    doc = fc.scrape(url, formats=["html"])
    html = doc.html if hasattr(doc, "html") else None
    
    content_clean = None
    publish_date = None
    
    if html:
        soup = BeautifulSoup(html, "html.parser")
        content_clean = extract_article_content(html)
        publish_date = extract_publish_date(soup)
    else:
        content_clean = getattr(doc, "markdown", "")
    
    # Fallback untuk tanggal dari metadata Firecrawl
    if not publish_date and hasattr(doc, "metadata"):
        meta = doc.metadata
        if hasattr(meta, "published_at"):
            publish_date = meta.published_at
        elif isinstance(meta, dict):
            publish_date = meta.get("published_at") or meta.get("publishedTime")
    
    # Scrape tags menggunakan Selenium
    print("Extracting tags...")
    tags = scrape_tags_with_selenium(url)
    
    return {
        "theme": theme,
        "title": article["title"],
        "link": url,
        "publish_date": publish_date,
        "tags": tags,
        "content": content_clean
    }

def scrape_theme(theme_url, theme_name, start_page=1, end_page=1):
    """Scrape articles from a specific theme"""
    print(f"\n{'='*60}")
    print(f"Starting scraping for theme: {theme_name}")
    print(f"Pages: {start_page} to {end_page}")
    print(f"{'='*60}\n")
    
    theme_results = []
    
    for page in range(start_page, end_page + 1):
        if page == 1:
            list_url = theme_url
        else:
            # Tambahkan /page/X/ di akhir URL
            list_url = theme_url.rstrip('/') + f"/page/{page}/"
        
        article_links = extract_article_links(list_url)
        
        for art in article_links:
            try:
                data = scrape_full_article(art, theme_name)
                theme_results.append(data)
                print(f"✓ Scraped: {data['title']}")
                print(f"  Date: {data['publish_date']}")
                print(f"  Tags: {', '.join(data['tags']) if data['tags'] else 'No tags'}")
                time.sleep(2)
            except Exception as ex:
                print(f"✗ Error scraping {art['link']}: {ex}")
    
    print(f"\n✓ Theme '{theme_name}' completed! Total articles: {len(theme_results)}\n")
    return theme_results

def scrape_multiple_themes(themes_config):
    """
    Scrape multiple themes
    
    Args:
        themes_config: List of dictionaries containing theme information
                      Format: [
                          {
                              "name": "perdata",
                              "url": "https://www.hukumonline.com/klinik/perdata/",
                              "start_page": 1,
                              "end_page": 2
                          },
                          ...
                      ]
    """
    all_results = []
    
    for theme in themes_config:
        theme_name = theme.get("name", "unknown")
        theme_url = theme.get("url")
        start_page = theme.get("start_page", 1)
        end_page = theme.get("end_page", 1)
        
        if not theme_url:
            print(f"⚠ Skipping theme '{theme_name}': No URL provided")
            continue
        
        try:
            results = scrape_theme(theme_url, theme_name, start_page, end_page)
            all_results.extend(results)
        except Exception as ex:
            print(f"✗ Error scraping theme '{theme_name}': {ex}")
    
    return all_results

if __name__ == "__main__":
    # Konfigurasi tema yang ingin di-scrape
    themes = [
        {
            "name": "hak asasi manusia",
            "url": "https://www.hukumonline.com/klinik/hak-asasi-manusia/",
            "start_page": 1,
            "end_page": 5
        }
        # Tambahkan tema lain sesuai kebutuhan
    ]
    
    # Jalankan scraping dan simpan per tema
    all_results = []
    saved_files = []
    
    for theme in themes:
        theme_name = theme.get("name", "unknown")
        theme_url = theme.get("url")
        start_page = theme.get("start_page", 1)
        end_page = theme.get("end_page", 1)
        
        if not theme_url:
            print(f"⚠ Skipping theme '{theme_name}': No URL provided")
            continue
        
        try:
            # Scrape tema
            results = scrape_theme(theme_url, theme_name, start_page, end_page)
            all_results.extend(results)
            
            # Simpan hasil per tema
            output_file = f"../result/hukumonline_{theme_name}_articles.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            
            saved_files.append({
                "theme": theme_name,
                "file": output_file,
                "count": len(results)
            })
            
            print(f"✓ Saved {theme_name} to: {output_file}")
            
        except Exception as ex:
            print(f"✗ Error scraping theme '{theme_name}': {ex}")
    
    # Summary
    print(f"\n{'='*60}")
    print("SCRAPING COMPLETED!")
    print(f"{'='*60}")
    print(f"Total articles scraped: {len(all_results)}")
    print(f"\nFiles saved:")
    for file_info in saved_files:
        print(f"  - {file_info['theme']}: {file_info['count']} articles → {file_info['file']}")
    print(f"{'='*60}\n")
"""
LEGO Deals Scraper for Amazon India and Flipkart
Finds LEGO sets with 40%-50% (or custom) discount.
"""

import sys
import re
import time
from typing import List, Dict, Optional
from curl_cffi import requests
from bs4 import BeautifulSoup

NON_LEGO_BRANDS = [
    'vikrida', 'yashoni', 'sky line', 'sky line ocean', 'satsun', 'sr toys', 
    'tarak', 'rvm toys', 'vaniha', 'willyard', 'sluban', 'lepin', 'mega bloks',
    'megabloks', 'toyrentto', 'magicwand', 'goolsky', 'dromida', 'mamatoyz',
    'architect series'
]

def clean_number(text: str) -> Optional[int]:
    """Extract integer number from string (e.g., '₹1,606' -> 1606)."""
    if not text:
        return None
    cleaned = re.sub(r'[^\d]', '', str(text))
    return int(cleaned) if cleaned else None

def is_official_lego(title: str, item_text: str = "") -> bool:
    """Strictly verify if a product is an authentic LEGO set."""
    if not title:
        return False
        
    title_clean = title.strip()
    title_lower = title_clean.lower()
    full_text_lower = (title_clean + " " + item_text).lower()

    # 1. Must contain LEGO as a standalone word
    if not re.search(r'\blego\b', title_clean, re.IGNORECASE):
        return False

    # 2. Must not be lunch box, bottle, bag, non-toy merchandise
    if re.search(r'\b(lunch box|tiffin|water bottle|school bag|backpack|pencil case|mizuware|tma enterprise)\b', full_text_lower, re.I):
        return False

    # 3. Must not be a compatible/knockoff phrasing
    if re.search(r'\b(compatible with|fits lego|for lego|lego-like|lego type|not lego|generic|diy building blocks)\b', full_text_lower, re.I):
        return False

    # 4. Must not belong to known third-party clone brands
    for brand in NON_LEGO_BRANDS:
        if brand in title_lower:
            return False

    # 5. Check prefix: genuine LEGO listings begin with LEGO or an official LEGO theme/number
    first_word = title_clean.split()[0].upper().rstrip(':,-')
    valid_starters = {'LEGO', 'LEGO®', 'DUPLO', 'TECHNIC', 'CREATOR', 'BRICK', 'CLASSIC'}
    if first_word not in valid_starters:
        if not re.search(r'^(LEGO\b|by LEGO\b)', title_clean, re.I):
            # If the first word is an uppercase company name like TMA, MIZUWARE, SR, reject it
            if len(first_word) > 1 and not first_word.isdigit():
                return False

    return True

def get_amazon_discount_facet(min_discount: int) -> str:
    """
    Select the safest Amazon.in discount facet that covers min_discount,
    ensuring that all matching deals (even 10%-25% discounts on F1/Supercars)
    are returned by Amazon so our scraper can accurately filter the exact range.
    """
    if min_discount >= 70:
        return "p_n_pct-off-with-tax%3A27060457031"  # 70% or more
    elif min_discount >= 60:
        return "p_n_pct-off-with-tax%3A27060456031"  # 60% or more
    elif min_discount >= 50:
        return "p_n_pct-off-with-tax%3A2665401031"   # 50% or more
    elif min_discount >= 35:
        return "p_n_pct-off-with-tax%3A2665402031"   # 35% or more
    elif min_discount >= 25:
        return "p_n_pct-off-with-tax%3A2665400031"   # 25% or more
    elif min_discount >= 10:
        return "p_n_pct-off-with-tax%3A2665399031"   # 10% or more
    else:
        return ""  # If min_discount < 10, don't restrict discount facet at all

def get_flipkart_discount_param(min_discount: int) -> str:
    """
    Select the safest Flipkart discount facet covering min_discount.
    """
    if min_discount >= 50:
        return "&p%5B%5D=facets.discount_range_v1%255B%255D%3D50%2525%2Bor%2Bmore"
    elif min_discount >= 40:
        return "&p%5B%5D=facets.discount_range_v1%255B%255D%3D40%2525%2Bor%2Bmore"
    elif min_discount >= 30:
        return "&p%5B%5D=facets.discount_range_v1%255B%255D%3D30%2525%2Bor%2Bmore"
    elif min_discount >= 20:
        return "&p%5B%5D=facets.discount_range_v1%255B%255D%3D20%2525%2Bor%2Bmore"
    elif min_discount >= 10:
        return "&p%5B%5D=facets.discount_range_v1%255B%255D%3D10%2525%2Bor%2Bmore"
    else:
        return ""

def scrape_amazon(
    query: str = "lego",
    min_discount: int = 40,
    max_discount: int = 50,
    official_only: bool = True,
    pages: int = 0,
    verbose: bool = True
) -> List[Dict]:
    """
    Scrape Amazon.in for LEGO deals within the discount range.
    Auto-detects total available catalog pages dynamically when pages=0 or pages='all'.
    """
    deals = []
    seen_asins = set()

    session = requests.Session()
    headers = {
        'Accept-Language': 'en-IN,en-GB;q=0.9,en;q=0.8',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    }
    session.headers.update(headers)

    # Warm up session with Amazon home page
    try:
        session.get('https://www.amazon.in/', impersonate='chrome124', timeout=10)
    except Exception:
        pass

    # Build dynamic facets
    brand_facet = "p_89%3ALEGO" if official_only else ""
    discount_facet = get_amazon_discount_facet(min_discount)
    
    facets = [f for f in [brand_facet, discount_facet] if f]
    rh_param = f"&rh={'%2C'.join(facets)}" if facets else ""

    # Dynamic pagination auto-detection
    auto_detect_all = (pages is None or pages <= 0 or str(pages).lower() in ('all', 'auto', '0'))
    max_scan_limit = 30 if auto_detect_all else int(pages)

    page = 1
    detected_total_pages = None

    while page <= max_scan_limit:
        url = f"https://www.amazon.in/s?k={query}{rh_param}&page={page}"
        if verbose:
            if detected_total_pages:
                print(f"[Amazon.in] Scanning Page {page}/{detected_total_pages}...")
            else:
                print(f"[Amazon.in] Scanning Page {page} (auto-detecting total)...")
            sys.stdout.flush()

        try:
            r = session.get(url, impersonate="chrome124", timeout=15)
            if r.status_code != 200:
                if verbose:
                    print(f"  [Amazon.in] Status code {r.status_code}, skipping page {page}.")
                page += 1
                continue

            soup = BeautifulSoup(r.text, 'html.parser')

            # Auto-detect total pages dynamically from Amazon pagination strip
            pag_strip = soup.find('span', {'class': 's-pagination-strip'})
            if pag_strip:
                page_items = pag_strip.find_all(class_=re.compile(r's-pagination-item'))
                page_numbers = [int(it.get_text(strip=True)) for it in page_items if it.get_text(strip=True).isdigit()]
                if page_numbers:
                    curr_max = max(page_numbers)
                    if detected_total_pages is None or curr_max > detected_total_pages:
                        detected_total_pages = curr_max
                        if auto_detect_all:
                            max_scan_limit = min(detected_total_pages, 30)
                        if verbose:
                            print(f"  [Amazon.in] Dynamic catalog detection: found {detected_total_pages} total pages.")

            items = soup.find_all('div', {'data-component-type': 's-search-result'})
            
            # If page 1 returned 0 items, retry up to 2 times with fresh session
            if not items and page == 1:
                for attempt in range(1, 3):
                    if verbose:
                        print(f"  [Amazon.in] Retrying Page 1 (attempt {attempt}) with fresh session...")
                    time.sleep(1.5)
                    session = requests.Session()
                    session.headers.update(headers)
                    try:
                        session.get('https://www.amazon.in/', impersonate='chrome124', timeout=10)
                    except Exception:
                        pass
                    r = session.get(url, impersonate="chrome124", timeout=15)
                    soup = BeautifulSoup(r.text, 'html.parser')
                    items = soup.find_all('div', {'data-component-type': 's-search-result'})
                    if items:
                        pag_strip = soup.find('span', {'class': 's-pagination-strip'})
                        if pag_strip:
                            page_items = pag_strip.find_all(class_=re.compile(r's-pagination-item'))
                            page_numbers = [int(it.get_text(strip=True)) for it in page_items if it.get_text(strip=True).isdigit()]
                            if page_numbers:
                                detected_total_pages = max(page_numbers)
                                if auto_detect_all:
                                    max_scan_limit = min(detected_total_pages, 30)
                        break

            if not items:
                if detected_total_pages and page < detected_total_pages:
                    if verbose:
                        print(f"  [Amazon.in] No items found on page {page}, continuing to page {page + 1}/{detected_total_pages}...")
                    page += 1
                    continue
                else:
                    if verbose:
                        print(f"  [Amazon.in] No items found on page {page}. Reached end of catalog.")
                    break

            for item in items:
                asin = item.get('data-asin', '').strip()
                if not asin or asin in seen_asins:
                    continue
                seen_asins.add(asin)

                # Extract product image and clean title from img alt
                img_el = item.find('img', class_='s-image')
                img_url = img_el.get('src', '') if img_el else ''
                img_alt = img_el.get('alt', '').strip() if img_el else ''
                img_alt = re.sub(r'^(Sponsored Ad\s*[-–:]\s*|Sponsored\s*[-–:]\s*)', '', img_alt, flags=re.IGNORECASE).strip()

                title = img_alt
                if not title or len(title) < 5 or title.lower() == 'lego':
                    for tc in item.select('h2 a span, a.a-text-normal span, h2 span'):
                        t = tc.get_text(strip=True)
                        if len(t) > len(title or ''):
                            title = t
                title = title or "LEGO Product"

                # Check Official LEGO filter if enabled
                if official_only:
                    if not is_official_lego(title, item.get_text()):
                        continue

                # Extract price
                p_whole = item.find('span', class_='a-price-whole')
                price = clean_number(p_whole.get_text()) if p_whole else None

                # Extract basis / MRP
                m_span = item.find('span', class_='a-price a-text-price')
                mrp = None
                if m_span:
                    off = m_span.find('span', class_='a-offscreen')
                    if off:
                        mrp = clean_number(off.get_text())

                # Sanity check on MRP
                if price and mrp and mrp > price * 3:
                    mrp = None

                # Extract discount
                discount = None
                disc_match = re.search(r'\((\d+)%\s*off\)', item.get_text(), re.IGNORECASE)
                if disc_match:
                    discount = int(disc_match.group(1))
                elif price and mrp and mrp > price:
                    discount = round((1 - price / mrp) * 100)

                # Filter strictly by user-defined discount range
                if discount is None:
                    continue
                if not (min_discount <= discount <= max_discount):
                    continue

                # If mrp wasn't in HTML, calculate from discount
                if not mrp and price and discount:
                    mrp = round(price / (1 - discount / 100))

                # Rating
                rating_el = item.find('span', class_='a-icon-alt')
                rating = rating_el.get_text(strip=True) if rating_el else ''

                product_url = f"https://www.amazon.in/dp/{asin}"

                deals.append({
                    'platform': 'Amazon.in',
                    'id': asin,
                    'title': title,
                    'price': price,
                    'mrp': mrp,
                    'discount': discount,
                    'savings': (mrp - price) if (mrp and price and mrp > price) else 0,
                    'rating': rating,
                    'image': img_url,
                    'url': product_url
                })

            # Check if there is an active Next page button on Amazon
            next_btn = soup.find('a', class_=re.compile(r's-pagination-next'))
            if not next_btn:
                if detected_total_pages and page < detected_total_pages:
                    pass
                else:
                    if verbose:
                        print(f"  [Amazon.in] Reached last page ({page}). Next button not available.")
                    break

        except Exception as e:
            if verbose:
                print(f"  [Amazon.in] Error fetching page {page}: {e}")

        page += 1
        time.sleep(0.5)

    return deals

def scrape_flipkart(
    query: str = "lego",
    min_discount: int = 40,
    max_discount: int = 50,
    official_only: bool = True,
    pages: int = 0,
    verbose: bool = True
) -> List[Dict]:
    """
    Scrape Flipkart for LEGO deals within the discount range.
    Auto-detects total available catalog pages dynamically.
    """
    deals = []
    seen_urls = set()

    session = requests.Session()
    headers = {
        'Accept-Language': 'en-IN,en;q=0.9',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/124.0.0.0 Safari/537.36'
    }

    # Brand facet & dynamic discount facet
    brand_param = "&p%5B%5D=facets.brand%255B%255D%3DLEGO" if official_only else ""
    discount_param = get_flipkart_discount_param(min_discount)

    auto_detect_all = (pages is None or pages <= 0 or str(pages).lower() in ('all', 'auto', '0'))
    max_scan_limit = 20 if auto_detect_all else int(pages)

    page = 1
    detected_total_pages = None

    while page <= max_scan_limit:
        url = f"https://www.flipkart.com/search?q={query}{brand_param}{discount_param}&page={page}"
        if verbose:
            if detected_total_pages:
                print(f"[Flipkart] Scanning Page {page}/{detected_total_pages}...")
            else:
                print(f"[Flipkart] Scanning Page {page} (auto-detecting total)...")
            sys.stdout.flush()

        try:
            r = session.get(url, impersonate="chrome124", headers=headers, timeout=15)
            if r.status_code != 200:
                if verbose:
                    print(f"  [Flipkart] Status code {r.status_code}, skipping page {page}.")
                page += 1
                continue

            soup = BeautifulSoup(r.text, 'html.parser')

            # Auto-detect total pages from nav
            if detected_total_pages is None:
                nav = soup.find('nav') or soup.find(class_=re.compile(r'pagination|_2miubQ|_1G92wA', re.I))
                if nav:
                    page_nums = [int(s) for s in re.findall(r'\b\d+\b', nav.get_text()) if int(s) < 100]
                    if page_nums:
                        detected_total_pages = max(page_nums)
                        if auto_detect_all:
                            max_scan_limit = min(detected_total_pages, 20)
                        if verbose:
                            print(f"  [Flipkart] Dynamic catalog detection: found {detected_total_pages} total pages.")

            # Find all links containing /p/
            cards = []
            for a in soup.find_all('a', href=True):
                if '/p/' in a['href'] and ('itm' in a['href'] or 'pid=' in a['href']):
                    parent = a.find_parent('div', class_=re.compile(r'(_1sdMkc|_4ddWXP|_75LdBv|col|slAVV4)')) or a.parent
                    if parent not in cards:
                        cards.append(parent)

            if not cards:
                has_products = any('/p/' in a.get('href', '') for a in soup.find_all('a', href=True))
                if not has_products:
                    if verbose:
                        print(f"  [Flipkart] Reached end of catalog at page {page}.")
                    break

            for card in (cards if cards else soup.find_all('div')):
                card_text = card.get_text(' | ', strip=True)
                if 'off' not in card_text.lower():
                    continue

                link_el = card.find('a', href=re.compile(r'/p/'))
                if not link_el:
                    continue
                href = link_el['href']
                if href in seen_urls:
                    continue
                seen_urls.add(href)
                full_url = f"https://www.flipkart.com{href}" if href.startswith('/') else href

                # Discount
                disc_match = re.search(r'(\d+)%\s*off', card_text, re.IGNORECASE)
                if not disc_match:
                    continue
                discount = int(disc_match.group(1))

                # Check discount filter
                if not (min_discount <= discount <= max_discount):
                    continue

                # Prices
                prices = re.findall(r'₹([\d,]+)', card_text)
                price = clean_number(prices[0]) if len(prices) > 0 else None
                mrp = clean_number(prices[1]) if len(prices) > 1 else None

                # Title
                title = None
                img = card.find('img', alt=True)
                if img and img.get('alt'):
                    title = img['alt']
                else:
                    for el in card.find_all(['a', 'div', 'span']):
                        t = el.get_text(strip=True)
                        if len(t) > 10 and not t.startswith('₹') and 'off' not in t.lower():
                            title = t
                            break
                title = title or "LEGO Set"

                # Check official LEGO brand
                if official_only:
                    if not is_official_lego(title, card_text):
                        continue

                # Fallback MRP calculation
                if not mrp and price and discount:
                    mrp = round(price / (1 - discount / 100))

                img_el = card.find('img', src=True)
                img_url = img_el['src'] if img_el else ''

                # Rating
                rating = ''
                rate_match = re.search(r'(\d\.\d)\s*★', card_text)
                if rate_match:
                    rating = rate_match.group(1)

                deals.append({
                    'platform': 'Flipkart',
                    'id': full_url,
                    'title': title,
                    'price': price,
                    'mrp': mrp,
                    'discount': discount,
                    'savings': (mrp - price) if (mrp and price and mrp > price) else 0,
                    'rating': rating,
                    'image': img_url,
                    'url': full_url
                })

            # Check if next page exists on Flipkart
            has_next = False
            for a in soup.find_all('a'):
                a_text = a.get_text().lower()
                if 'next' in a_text or (a.find('span') and 'next' in a.find('span').get_text().lower()):
                    has_next = True
                    break

            if not has_next:
                if verbose:
                    print(f"  [Flipkart] Reached last page ({page}). Next button not present.")
                break

        except Exception as e:
            if verbose:
                print(f"  [Flipkart] Error fetching page {page}: {e}")

        page += 1
        time.sleep(0.5)

    return deals

def get_lego_deals(
    min_discount: int = 40,
    max_discount: int = 50,
    platform: str = "both",
    official_only: bool = True,
    pages: int = 0,
    verbose: bool = True
) -> List[Dict]:
    """Fetch deals from specified platform(s) with official LEGO filter by default."""
    all_deals = []
    
    if platform.lower() in ("amazon", "both"):
        amazon_deals = scrape_amazon(
            min_discount=min_discount,
            max_discount=max_discount,
            official_only=official_only,
            pages=pages,
            verbose=verbose
        )
        all_deals.extend(amazon_deals)
        
    if platform.lower() in ("flipkart", "both"):
        flipkart_deals = scrape_flipkart(
            min_discount=min_discount,
            max_discount=max_discount,
            official_only=official_only,
            pages=pages,
            verbose=verbose
        )
        all_deals.extend(flipkart_deals)
        
    # Sort deals by discount descending, then savings descending
    all_deals.sort(key=lambda x: (x.get('discount') or 0, x.get('savings') or 0), reverse=True)
    return all_deals

def categorize_lego_car(title: str) -> str:
    """Categorize car based on model keywords."""
    tl = title.lower()
    if any(k in tl for k in ['f1', 'formula 1', 'formula e', 'red bull', 'rb20', 'sf-24', 'sf24', 'vcarb', 'a524', 'mercedes-amg f1', 'w14', 'race car driver', 'alpine', 'monoposto']):
        return "Formula 1"
    if any(k in tl for k in ['batman', 'batmobile', 'fast and furious', 'fast & furious', 'skyline', 'time machine', 'delorean', '007', 'aston martin', 'defender', 'land rover', 'ghostbusters', 'ecto']):
        return "Movie & Iconic"
    if 'technic' in tl:
        return "Technic"
    if any(k in tl for k in ['ferrari', 'lamborghini', 'bugatti', 'porsche', 'mclaren', 'koenigsegg', 'ford gt', 'mustang', 'corvette', 'hypercar', 'stradale', 'competizione', 'bolide', 'supra', 'lambo']):
        return "Supercar"
    return "Sports Car"

_CARS_CACHE = {
    'timestamp': 0,
    'deals': []
}

def scrape_amazon_cars(pages: int = 2, verbose: bool = True) -> List[Dict]:
    """Scrape LEGO Cars from Amazon India (F1, Speed Champions, Technic, Supercars)."""
    cars = []
    seen_asins = set()

    session = requests.Session()
    headers = {
        'Accept-Language': 'en-IN,en-GB;q=0.9,en;q=0.8',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    }
    session.headers.update(headers)

    try:
        session.get('https://www.amazon.in/', impersonate='chrome124', timeout=10)
    except Exception:
        pass

    queries = ["lego+speed+champions", "lego+f1+car", "lego+technic+car"]
    for q in queries:
        for page in range(1, pages + 1):
            url = f"https://www.amazon.in/s?k={q}&page={page}"
            if verbose:
                print(f"[Amazon.in Cars] Query: {q}, Page {page}/{pages}...")

            try:
                r = session.get(url, impersonate="chrome124", timeout=15)
                if r.status_code != 200:
                    continue

                soup = BeautifulSoup(r.text, 'html.parser')
                items = soup.find_all('div', {'data-component-type': 's-search-result'})
                if not items:
                    break

                for item in items:
                    asin = item.get('data-asin', '').strip()
                    if not asin or asin in seen_asins:
                        continue
                    seen_asins.add(asin)

                    img_el = item.find('img', class_='s-image')
                    img_url = img_el.get('src', '') if img_el else ''
                    img_alt = img_el.get('alt', '').strip() if img_el else ''
                    img_alt = re.sub(r'^(Sponsored Ad\s*[-–:]\s*|Sponsored\s*[-–:]\s*)', '', img_alt, flags=re.IGNORECASE).strip()

                    title = img_alt
                    if not title or len(title) < 5 or title.lower() == 'lego':
                        for tc in item.select('h2 a span, a.a-text-normal span, h2 span'):
                            t = tc.get_text(strip=True)
                            if len(t) > len(title or ''):
                                title = t
                    title = title or "LEGO Car"

                    # Only official LEGO
                    if not is_official_lego(title, item.get_text()):
                        continue

                    # Filter: ensure it's a vehicle/car/F1
                    title_l = title.lower()
                    car_keywords = ['car', 'f1', 'speed', 'racing', 'vehicle', 'ferrari', 'lamborghini', 'bugatti', 'porsche', 'mclaren', 'nissan', 'bmw', 'mercedes', 'batmobile', 'defender', 'corvette', 'mustang', 'supra', 'bolide', 'stradale']
                    if not any(k in title_l for k in car_keywords):
                        continue

                    p_whole = item.find('span', class_='a-price-whole')
                    price = clean_number(p_whole.get_text()) if p_whole else None

                    m_span = item.find('span', class_='a-price a-text-price')
                    mrp = None
                    if m_span:
                        off = m_span.find('span', class_='a-offscreen')
                        if off:
                            mrp = clean_number(off.get_text())

                    disc_match = re.search(r'\((\d+)%\s*off\)', item.get_text())
                    discount = int(disc_match.group(1)) if disc_match else (round((1 - price / mrp) * 100) if (price and mrp and mrp > price) else 0)

                    rating_el = item.find('span', class_='a-icon-alt')
                    rating = rating_el.get_text(strip=True) if rating_el else ''

                    category = categorize_lego_car(title)

                    cars.append({
                        'platform': 'Amazon.in',
                        'id': asin,
                        'title': title,
                        'price': price,
                        'mrp': mrp or price,
                        'discount': discount,
                        'savings': (mrp - price) if (mrp and price and mrp > price) else 0,
                        'category': category,
                        'rating': rating,
                        'image': img_url,
                        'url': f"https://www.amazon.in/dp/{asin}"
                    })
            except Exception as e:
                if verbose:
                    print(f"  [Amazon.in Cars] Error: {e}")

            time.sleep(1)

    return cars

def scrape_flipkart_cars(pages: int = 2, verbose: bool = True) -> List[Dict]:
    """Scrape LEGO Cars from Flipkart (Speed Champions, Technic, F1, Supercars)."""
    cars = []
    seen_urls = set()

    session = requests.Session()
    headers = {
        'Accept-Language': 'en-IN,en;q=0.9',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
    }

    queries = ["lego+speed+champions", "lego+f1+car", "lego+technic+car"]
    for q in queries:
        for page in range(1, pages + 1):
            url = f"https://www.flipkart.com/search?q={q}&p%5B%5D=facets.brand%255B%255D%3DLEGO&page={page}"
            if verbose:
                print(f"[Flipkart Cars] Query: {q}, Page {page}/{pages}...")

            try:
                r = session.get(url, impersonate="chrome124", headers=headers, timeout=15)
                if r.status_code != 200:
                    continue

                soup = BeautifulSoup(r.text, 'html.parser')
                cards = []
                for a in soup.find_all('a', href=True):
                    if '/p/' in a['href'] and ('itm' in a['href'] or 'pid=' in a['href']):
                        parent = a.find_parent('div', class_=re.compile(r'(_1sdMkc|_4ddWXP|_75LdBv|col|slAVV4)')) or a.parent
                        if parent not in cards:
                            cards.append(parent)

                if not cards:
                    break

                for card in cards:
                    card_text = card.get_text(' | ', strip=True)
                    link_el = card.find('a', href=re.compile(r'/p/'))
                    if not link_el:
                        continue
                    href = link_el['href']
                    if href in seen_urls:
                        continue
                    seen_urls.add(href)
                    full_url = f"https://www.flipkart.com{href}" if href.startswith('/') else href

                    img = card.find('img', alt=True)
                    title = img['alt'] if img else link_el.get_text(strip=True)

                    if not is_official_lego(title, card_text):
                        continue

                    # Filter: ensure it's a vehicle/car/F1
                    title_l = title.lower()
                    car_keywords = ['car', 'f1', 'speed', 'racing', 'vehicle', 'ferrari', 'lamborghini', 'bugatti', 'porsche', 'mclaren', 'nissan', 'bmw', 'mercedes', 'batmobile', 'defender', 'corvette', 'mustang', 'supra', 'bolide', 'stradale', 'dragster']
                    if not any(k in title_l for k in car_keywords):
                        continue

                    prices = re.findall(r'₹([\d,]+)', card_text)
                    price = clean_number(prices[0]) if len(prices) > 0 else None
                    mrp = clean_number(prices[1]) if len(prices) > 1 else price

                    disc_match = re.search(r'(\d+)%\s*off', card_text, re.IGNORECASE)
                    discount = int(disc_match.group(1)) if disc_match else (round((1 - price / mrp) * 100) if (price and mrp and mrp > price) else 0)

                    rating_match = re.search(r'(\d\.\d)\s*★?', card_text)
                    rating = f"{rating_match.group(1)} ★" if rating_match else ""

                    img_el = card.find('img')
                    img_url = img_el.get('src') or img_el.get('data-src') if img_el else ''

                    category = categorize_lego_car(title)

                    cars.append({
                        'platform': 'Flipkart',
                        'id': href.split('pid=')[-1].split('&')[0] if 'pid=' in href else href[:30],
                        'title': title,
                        'price': price,
                        'mrp': mrp or price,
                        'discount': discount,
                        'savings': (mrp - price) if (mrp and price and mrp > price) else 0,
                        'category': category,
                        'rating': rating,
                        'image': img_url,
                        'url': full_url
                    })
            except Exception as e:
                if verbose:
                    print(f"  [Flipkart Cars] Error: {e}")

            time.sleep(1)

    return cars

def get_lego_cars(
    platform: str = "both",
    category: str = "all",
    pages: int = 2,
    force_refresh: bool = False,
    verbose: bool = True
) -> List[Dict]:
    """Get LEGO cars with independent platform caching and category filtering."""
    global _CARS_CACHE
    now = time.time()

    plat = platform.lower()
    needs_amazon = plat in ("amazon", "both")
    needs_flipkart = plat in ("flipkart", "both")

    # Cache Amazon independently
    if needs_amazon:
        amz_cache = _CARS_CACHE.get('amazon', {'timestamp': 0, 'data': []})
        if force_refresh or (now - amz_cache.get('timestamp', 0) > 900) or not amz_cache.get('data'):
            if verbose:
                print("[Cars] Fetching fresh LEGO cars from Amazon.in...")
            amz_data = scrape_amazon_cars(pages=pages, verbose=verbose)
            _CARS_CACHE['amazon'] = {'timestamp': now, 'data': amz_data}

    # Cache Flipkart independently
    if needs_flipkart:
        flp_cache = _CARS_CACHE.get('flipkart', {'timestamp': 0, 'data': []})
        if force_refresh or (now - flp_cache.get('timestamp', 0) > 900) or not flp_cache.get('data'):
            if verbose:
                print("[Cars] Fetching fresh LEGO cars from Flipkart...")
            flp_data = scrape_flipkart_cars(pages=pages, verbose=verbose)
            _CARS_CACHE['flipkart'] = {'timestamp': now, 'data': flp_data}

    results = []
    if needs_amazon:
        results.extend(_CARS_CACHE.get('amazon', {}).get('data', []))
    if needs_flipkart:
        results.extend(_CARS_CACHE.get('flipkart', {}).get('data', []))

    # Filter category
    if category.lower() not in ("all", ""):
        results = [c for c in results if c.get('category', '').lower() == category.lower()]

    return results


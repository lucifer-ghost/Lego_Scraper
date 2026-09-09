#!/usr/bin/env python3
"""
Find LEGO Deals - Scrape Amazon India & Flipkart for 40%-50% discounts
Usage:
    python find_lego_deals.py
    python find_lego_deals.py --min-discount 40 --max-discount 50
    python find_lego_deals.py --platform amazon --official-only
    python find_lego_deals.py --web
"""

import sys
import os
import argparse
import csv
import json
from scraper import get_lego_deals

# Fix Unicode encoding on Windows terminals
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# ANSI Color codes for clean terminal output
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

def format_inr(val):
    if val is None:
        return "N/A"
    return f"₹{val:,}"

def print_banner(min_d, max_d, platform, official):
    print(f"{BOLD}{CYAN}========================================================================{RESET}")
    print(f"{BOLD}{YELLOW} 🧱 LEGO DEAL FINDER (Amazon India & Flipkart) {RESET}")
    print(f" Target Discount: {GREEN}{min_d}% - {max_d}% OFF{RESET}")
    print(f" Platform       : {CYAN}{platform.upper()}{RESET}")
    print(f" Filter         : {YELLOW}{'Official LEGO Brand Only' if official else 'All Lego & Compatible Building Sets'}{RESET}")
    print(f"{BOLD}{CYAN}========================================================================{RESET}\n")

def print_deals_table(deals):
    if not deals:
        print(f"{YELLOW}No matching deals found for this criteria.{RESET}")
        print(f"{DIM}Tip: Try relaxing the discount filter with --min-discount 30 or omitting --official-only.{RESET}")
        return

    print(f"\n{BOLD}{GREEN}Found {len(deals)} LEGO Deals Matching Your Criteria:{RESET}\n")
    print(f"{BOLD}{'PLATFORM':<12} {'DISCOUNT':<10} {'PRICE':<12} {'MRP':<12} {'SAVINGS':<12} {'PRODUCT TITLE'}{RESET}")
    print("-" * 90)

    for d in deals:
        platform_color = CYAN if d['platform'] == 'Amazon.in' else YELLOW
        disc_str = f"{BOLD}{GREEN}{d['discount']}% OFF{RESET}"
        price_str = format_inr(d['price'])
        mrp_str = format_inr(d['mrp'])
        savings_str = f"{GREEN}+{format_inr(d['savings'])}{RESET}" if d['savings'] else "-"
        title_snippet = d['title'][:48] + "..." if len(d['title']) > 48 else d['title']
        
        print(f"{platform_color}{d['platform']:<12}{RESET} {disc_str:<19} {price_str:<12} {mrp_str:<12} {savings_str:<21} {title_snippet}")
        print(f"   {DIM}🔗 Link:{RESET} {d['url']}")

    print("\n" + "=" * 90)

def export_to_csv(deals, filepath="lego_deals.csv"):
    if not deals:
        return
    keys = ['platform', 'discount', 'price', 'mrp', 'savings', 'title', 'rating', 'url', 'image']
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys, extrasaction='ignore')
        writer.writeheader()
        for d in deals:
            writer.writerow(d)
    print(f"{GREEN}✓ Successfully saved {len(deals)} deals to {BOLD}{filepath}{RESET}")

def export_to_json(deals, filepath="lego_deals.json"):
    if not deals:
        return
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(deals, f, indent=2, ensure_ascii=False)
    print(f"{GREEN}✓ Successfully saved {len(deals)} deals to {BOLD}{filepath}{RESET}")

def main():
    parser = argparse.ArgumentParser(description="Find LEGO sets with 40%-50% discount on Amazon India and Flipkart.")
    parser.add_argument("--min-discount", type=int, default=40, help="Minimum discount percentage (default: 40)")
    parser.add_argument("--max-discount", type=int, default=50, help="Maximum discount percentage (default: 50)")
    parser.add_argument("--platform", choices=["amazon", "flipkart", "both"], default="both", help="Platform to scan (default: both)")
    parser.add_argument("--all-brands", action="store_true", default=False, help="Include third-party compatible building blocks (by default only Official LEGO is scanned)")
    parser.add_argument("--official-only", action="store_true", default=True, help="Filter strictly for official LEGO brand (enabled by default)")
    parser.add_argument("--pages", type=int, default=7, help="Number of search result pages to scan per platform (default: 7 - scans all pages)")
    parser.add_argument("--csv", type=str, default="lego_deals.csv", help="CSV filename to export deals to (default: lego_deals.csv)")
    parser.add_argument("--json", type=str, default=None, help="Optional JSON filename to export deals to")
    parser.add_argument("--web", action="store_true", help="Launch interactive browser dashboard")
    parser.add_argument("--port", type=int, default=5000, help="Port for web dashboard (default: 5000)")

    args = parser.parse_args()

    # Determine official_only
    official_only = not args.all_brands if args.all_brands else True

    if args.web:
        from web_app import run_server
        run_server(port=args.port)
        return

    print_banner(args.min_discount, args.max_discount, args.platform, official_only)

    deals = get_lego_deals(
        min_discount=args.min_discount,
        max_discount=args.max_discount,
        platform=args.platform,
        official_only=official_only,
        pages=args.pages,
        verbose=True
    )

    print_deals_table(deals)

    if deals and args.csv:
        export_to_csv(deals, args.csv)
        
    if deals and args.json:
        export_to_json(deals, args.json)

if __name__ == "__main__":
    main()

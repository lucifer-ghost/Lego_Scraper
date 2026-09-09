# 🧱 LEGO Deals Finder (Amazon India & Flipkart)

A Python tool and web dashboard to automatically find **LEGO sets with 40%–50% discount** (or any custom discount range) on **Amazon India (Amazon.in)** and **Flipkart**.

---

## ⚡ Quick Direct Store Links (No Code Needed)

If you just want to browse directly in your browser:

- 🛒 **Amazon.in (Official LEGO with 35%–50%+ Discount):**  
  [https://www.amazon.in/s?k=lego&rh=p_89%3ALEGO%2Cp_n_pct-off-with-tax%3A2665402031](https://www.amazon.in/s?k=lego&rh=p_89%3ALEGO%2Cp_n_pct-off-with-tax%3A2665402031)

- 🛒 **Amazon.in (Official LEGO with 50%+ Discount):**  
  [https://www.amazon.in/s?k=lego&rh=p_89%3ALEGO%2Cp_n_pct-off-with-tax%3A2665401031](https://www.amazon.in/s?k=lego&rh=p_89%3ALEGO%2Cp_n_pct-off-with-tax%3A2665401031)

- 🛍️ **Flipkart (Lego & Building Sets with 40%+ Discount):**  
  [https://www.flipkart.com/search?q=lego&p%5B%5D=facets.discount_range_v1%255B%255D%3D40%2525%2Bor%2Bmore](https://www.flipkart.com/search?q=lego&p%5B%5D=facets.discount_range_v1%255B%255D%3D40%2525%2Bor%2Bmore)

---

## 🚀 How to Run the Code

### 1. Requirements
The dependencies (`curl_cffi` and `beautifulsoup4`) are already installed. If running on another machine:
```bash
pip install -r requirements.txt
```

---

### 2. Option A: Interactive React Web App (Primary & Recommended)

Launch the visual dashboard in your browser:
```bash
python web_app.py
```

- Opens **`http://localhost:5000`** in your browser.
- **Modern React 18 SPA** with sleek dark aesthetics, micro-animations, and glassmorphism.
- **Two Primary Tabs**:
  1. **🔥 40%–50% Deals Radar**:
     - **🛡️ "Official LEGO Only" is ON by default** with a responsive toggle switch.
     - Adjust discount sliders (**40% to 50%**, or any custom range).
     - Scans up to all 7 pages across Amazon India and Flipkart.
     - One-click **"Export CSV"** button.
  2. **🏎️ LEGO Cars & F1 (Dedicated Car Section)**:
     - Shows all official LEGO cars without discount constraints.
     - **Separate store sections: Amazon.in is the DEFAULT store**, with Flipkart and Both stores toggle.
     - Filter by category: `🏎️ All Cars`, `🏁 Formula 1 (F1)`, `🚀 Supercars`, `⚙️ Technic Cars`, `🎬 Movie & Iconic Cars`.
     - Fast instant loading with pre-warmed caching.


---

### 3. Option B: Command Line Interface (CLI)

Run directly in PowerShell / Command Prompt:

```bash
# Standard 40% - 50% discount search (Official LEGO enabled by default):
python find_lego_deals.py

# Include third-party compatible building blocks as well:
python find_lego_deals.py --all-brands

# Custom discount range (e.g., 35% to 60%):
python find_lego_deals.py --min-discount 35 --max-discount 60

# Amazon India only:
python find_lego_deals.py --platform amazon

# Flipkart only:
python find_lego_deals.py --platform flipkart

# Deep scan (3 pages per store):
python find_lego_deals.py --pages 3 --csv my_lego_deals.csv
```

---

## 📁 Output

- The script automatically outputs results to the terminal with colors and links.
- Automatically exports results to `lego_deals.csv` with:
  - Platform (`Amazon.in` or `Flipkart`)
  - Discount %
  - Deal Price (₹)
  - Original MRP (₹)
  - Savings (₹)
  - Product Title
  - Product URL

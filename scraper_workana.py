"""Workana public projects scraper for market analysis.

Usage:
    python scraper_workana.py --pages 3
    python scraper_workana.py --pages 5 --category it-programming --country MX --output data.csv
    python scraper_workana.py --pages 2 --keyword python --output data.json

Outputs CSV/JSON ready for Power BI.
Respects robots.txt: only reads public /jobs pages, with pauses between pages.

Note: the site is scraped with the Spanish UI (language=es), so literals
parsed from page text (e.g. "menos de", "más de", "/hora") are in Spanish.
"""
import argparse
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

BASE = "https://www.workana.com"


def build_url(page: int, category: str = "", country: str = "",
              keyword: str = "", skill: str = "") -> str:
    params = ["language=es"]
    if category:
        params.append(f"category={category}")
    if country:
        params.append(f"country={country}")
    if skill:
        params.append(f"skills={skill}")
    if keyword:
        params.append(f"query={keyword}")
    params.append(f"page={page}")
    return f"{BASE}/jobs?" + "&".join(params)


def parse_budget(text: str):
    """Return (min, max, currency, is_hourly) from text like 'USD 100 - 250',
    'Menos de USD 15 / hora' or 'Más de USD 3.000' (dot as thousands separator)."""
    if not text:
        return None, None, None, False
    t = text.strip()
    is_hourly = bool(re.search(r"/\s*hora|hour|hr", t, re.I))
    currency = "USD" if "USD" in t.upper() else ("MXN" if "MXN" in t.upper() else None)
    # normalize thousands separators: 3.000 / 3,000 -> 3000
    t2 = re.sub(r"\.(?=\d{3}\b)", "", t)
    t2 = re.sub(r",(?=\d{3}\b)", "", t2)
    # remaining decimal separator -> dot
    t2 = t2.replace(",", ".")
    nums = [float(n) for n in re.findall(r"\d+(?:\.\d+)?", t2)]
    nums = [n for n in nums if n < 10_000_000]
    if not nums:
        return None, None, currency, is_hourly
    low = t.lower()
    if "menos de" in low:
        return None, nums[0], currency, is_hourly
    if "más de" in low or "mas de" in low:
        return nums[0], None, currency, is_hourly
    if len(nums) >= 2:
        return nums[0], nums[1], currency, is_hourly
    return nums[0], nums[0], currency, is_hourly


def extract_projects(html: str):
    soup = BeautifulSoup(html, "lxml")
    items = soup.select("div.project-item")
    rows = []
    for it in items:
        a = it.select_one("h2.project-title a[href*='/job/']")
        if not a:
            continue
        href = a.get("href", "")
        slug = href.strip("/").split("/")[-1]
        title = a.get_text(strip=True)

        pub = it.select_one("span.date")
        posted = pub.get_text(strip=True) if pub else ""
        bids_el = it.select_one("span.bids")
        bids = None
        if bids_el:
            m = re.search(r"(\d+)", bids_el.get_text())
            bids = int(m.group(1)) if m else 0

        desc_el = it.select_one("div.html-desc p.text-expander-content span")
        description = desc_el.get_text(strip=True) if desc_el else ""

        skills = [h.get_text(strip=True) for h in it.select("div.skills a.skill h3")]

        client_el = it.select_one("span.author-info span")
        client = client_el.get_text(strip=True) if client_el else ""
        country_el = it.select_one("span.country-name a")
        country = country_el.get_text(strip=True) if country_el else ""
        country_code = ""
        if country_el and country_el.get("href"):
            m = re.search(r"country=([A-Z]{2})", country_el["href"])
            country_code = m.group(1) if m else ""
        payment_verified = bool(it.select_one("span.payment-verified"))

        budget_el = it.select_one("p.budget span.values span")
        budget_text = budget_el.get_text(strip=True) if budget_el else ""
        budget_text = re.split(r"Recuerda", budget_text)[0].strip()
        bmin, bmax, currency, is_hourly = parse_budget(budget_text)

        featured = "project-item-featured" in (it.get("class") or [])

        rows.append({
            "slug": slug,
            "title": title,
            "url": BASE + href if href.startswith("/") else href,
            "description": description,
            "budget_text": budget_text,
            "budget_min": bmin,
            "budget_max": bmax,
            "currency": currency,
            "is_hourly": is_hourly,
            "posted": posted,
            "bids": bids,
            "skills": "; ".join(skills),
            "client": client,
            "country": country,
            "country_code": country_code,
            "payment_verified": payment_verified,
            "featured": featured,
            "scraped_at": datetime.now(timezone.utc).isoformat(),
        })
    return rows


def scrape(pages: int, category="", country="", keyword="", skill="", pause=3.0):
    all_rows = []
    seen = set()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # browser = p.chromium.launch(headless=False, slow_mo=100)
        for n in range(1, pages + 1):
            url = build_url(n, category, country, keyword, skill)
            print(f"[{n}/{pages}] {url}")
            # fresh context per page: avoids blocks on sequential navigation
            ctx = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36")
            pg = ctx.new_page()
            ok = False
            for attempt in range(3):
                try:
                    pg.goto(url, wait_until="domcontentloaded", timeout=45000)
                    pg.wait_for_selector("div.project-item", timeout=30000)
                    pg.wait_for_timeout(2000)
                    ok = True
                    break
                except Exception:
                    print(f"  attempt {attempt+1} failed, retrying...")
                    pg.wait_for_timeout(8000)
            if not ok:
                print("  Could not load, skipping page.")
                ctx.close()
                continue
            rows = extract_projects(pg.content())
            ctx.close()
            new_rows = [r for r in rows if r["slug"] not in seen]
            print(f"  -> {len(rows)} projects ({len(new_rows)} new)")
            if not rows:
                print("  No results, stopping.")
                break
            if not new_rows:
                print("  Repeated page (end of listing), stopping.")
                break
            for r in new_rows:
                seen.add(r["slug"])
            all_rows.extend(new_rows)
            time.sleep(pause)
        browser.close()
    return all_rows


def summarize(df: pd.DataFrame):
    print("\n=== SUMMARY ===")
    print(f"Projects: {len(df)}")
    if df.empty:
        return
    print("\nTop countries:")
    print(df["country"].value_counts().head(10).to_string())
    print("\nTop skills:")
    skills = df["skills"].str.split("; ").explode().str.strip()
    skills = skills[skills != ""]
    print(skills.value_counts().head(15).to_string())
    print("\nBids (mean/median):")
    print(df["bids"].describe()[["mean", "50%", "max"]].to_string())
    fixed = df[~df["is_hourly"] & df["budget_max"].notna()]
    if not fixed.empty:
        print(f"\nFixed budget (max): mean {fixed['budget_max'].mean():.0f}, median {fixed['budget_max'].median():.0f}")
    hourly = df[df["is_hourly"] & df["budget_max"].notna()]
    if not hourly.empty:
        print(f"Hourly rate (max): mean {hourly['budget_max'].mean():.1f}")


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Workana /jobs scraper")
    ap.add_argument("--pages", type=int, default=3, help="Number of pages (~9 projects each)")
    ap.add_argument("--category", default="", help="E.g.: it-programming, design-multimedia, sales-marketing")
    ap.add_argument("--country", default="", help="2-letter code: MX, AR, CO, ES...")
    ap.add_argument("--keyword", default="", help="Search keyword")
    ap.add_argument("--skill", default="", help="E.g.: python, logo-design-1")
    ap.add_argument("--output", default="workana_projects.csv", help="Output file (.csv or .json)")
    args = ap.parse_args()

    rows = scrape(args.pages, args.category, args.country, args.keyword, args.skill)
    rows = [{"id": i, **r} for i, r in enumerate(rows, 1)]
    # tag each row with the category filter used (empty = all categories)
    for r in rows:
        r["category"] = args.category
    df = pd.DataFrame(rows)
    out = Path(args.output)
    if out.suffix.lower() == ".json":
        out.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    else:
        df.to_csv(out, index=False, encoding="utf-8-sig")
        # mirror JSON copy for Power BI / automation
        out.with_suffix(".json").write_text(
            json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nSaved: {out} ({len(df)} rows)")
    summarize(df)


if __name__ == "__main__":
    main()

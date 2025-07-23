from pathlib import Path
from bs4 import BeautifulSoup
import pandas as pd
import json
import unicodedata
import re
from datetime import datetime
import argparse

def parse_nss_html(item):
    a_tag = item.find('a', class_='basicProductCard_link__urzND')
    rank = a_tag.get('data-shp-contents-rank')
    is_ad = a_tag.get('data-shp-contents-grp')
    product_url = a_tag.get('href')

    product_id = None
    if a_tag.has_attr('data-shp-contents-dtl'):
        try:
            shp_data = json.loads(a_tag['data-shp-contents-dtl'])
            for sd in shp_data:
                if sd.get('key') == 'chnl_prod_no':
                    product_id = sd.get('value')
        except Exception:
            pass

    brand_tag = item.find('span', class_='productCardMallLink_mall_name__5oWPw')
    brand = brand_tag.get_text(strip=True) if brand_tag else None

    title_tag = item.find('strong', class_='productCardTitle_product_card_title__eQupA')
    product_title = title_tag.get_text(strip=True) if title_tag else None

    review_cnt = avg_rating = None
    review_box = item.find('div', class_='productCardReview_product_card_review__Oiv_T')
    if review_box:
        rating_tag = review_box.find('span', class_='productCardReview_star__7iHNO')
        avg_rating = rating_tag.get_text(strip=True).replace('별점', '') if rating_tag else None
        review_count_tag = review_box.find_all('span', class_='productCardReview_text__A9N9N')
        if len(review_count_tag) > 1:
            review_cnt = review_count_tag[1].get_text(strip=True).replace('리뷰', '').strip()

    return rank, is_ad, product_title, product_id, brand, review_cnt, avg_rating, product_url

def parse_review_count(raw):
    if pd.isna(raw):
        return None
    raw = str(raw).replace('(', '').replace(')', '').replace(',', '').strip()
    if '만' in raw:
        try:
            num = float(raw.replace('만', ''))
            return int(num * 10000)
        except ValueError:
            return None
    return int(raw) if raw.isdigit() else None

def parse_rating(raw):
    if pd.isna(raw):
        return None
    match = re.search(r'(\d+\.\d+)', str(raw))
    return float(match.group(1)) if match else None

def process_html_file(file_path: Path, collected_dt: str, platform: str = "네이버플러스스토어"):
    results = []
    keyword = file_path.stem.strip()
    keyword = unicodedata.normalize("NFC", str(keyword))

    with file_path.open('r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    product_list = soup.find_all('div', class_='basicProductCard_basic_product_card__TdrHT')
    top10_items = product_list[:10]

    for idx, item in enumerate(top10_items, 1):
        result = parse_nss_html(item)
        rank, is_ad, product_title, product_id, brand, review_cnt, avg_rating, product_url = result

        results.append({
            'keyword': keyword,
            'rank': idx,
            'is_ad': True if is_ad == 'ad' else False,
            'platform': platform,
            'brand': brand,
            'product_title': product_title,
            'product_id': product_id,
            'review_cnt': parse_review_count(review_cnt),
            'avg_rating': parse_rating(avg_rating),
            'product_url': product_url,
            'collected_dt': pd.to_datetime(collected_dt).date()
        })

    return results

def process_html_folder(input_folder: Path, output_csv: Path, collected_dt: str):
    all_records = []
    for file in input_folder.glob("*.html"):
        records = process_html_file(file, collected_dt)
        all_records.extend(records)

    df = pd.DataFrame(all_records)
    df = df.astype({
        'rank': 'int64',
        'product_id': 'string',
        'review_cnt': 'Int64',
        'avg_rating': 'float64'
    })

    df = df[['keyword', 'rank', 'is_ad', 'platform', 'brand', 'product_title',
             'product_id', 'review_cnt', 'avg_rating', 'product_url', 'collected_dt']]
    
    df["brand"] = df["brand"].replace(r"\s+", " ", regex=True)
    df["product_title"] = df["product_title"].replace(r"\s+", " ", regex=True)

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_csv, index=False, encoding='utf-8-sig')
    print(f"[저장 완료] {output_csv.as_posix()}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", type=str, help="수집 대상 날짜 (YYYYMMDD)", default=datetime.today().strftime("%Y%m%d"))
    args = parser.parse_args()

    target_date = args.date
    search_rank_dir = Path(__file__).resolve().parent.parent
    input_dir = search_rank_dir / "html" / "smartstore" / f"html_{target_date}"
    output_file = search_rank_dir / "data" / "smartstore" / f"search_rank_nss_{target_date}.csv"

    process_html_folder(input_dir, output_file, collected_dt=target_date)

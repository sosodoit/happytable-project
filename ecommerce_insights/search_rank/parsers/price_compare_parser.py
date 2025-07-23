from pathlib import Path
from bs4 import BeautifulSoup
import pandas as pd
import json
import unicodedata
import re
from datetime import datetime
import argparse

def parse_ad_product(item):
    kind = '광고상품'
    title_tag = item.find('div', class_='adProduct_title__fsQU6')
    product_title = title_tag.get_text(strip=True)

    a_tag = title_tag.find('a')
    rank = a_tag.get('data-shp-contents-rank')
    is_ad = a_tag.get('data-shp-contents-grp')

    product_id = product_url = None
    if a_tag and a_tag.has_attr('data-shp-contents-dtl'):
        shp_data = json.loads(a_tag['data-shp-contents-dtl'])
        for sd in shp_data:
            key = sd.get('key')
            value = sd.get('value')
            if key == 'chnl_prod_no':
                product_id = value
            elif key == 'nv_mid' and product_id is None:
                product_id = value 
            elif key == 'href':
                product_url = value

    if not product_url:
        product_url = a_tag.get('href')

    mall_title_div = item.find('div', class_='adProduct_mall_title__Ivl98')
    brand = mall_title_div.find('a').get_text(strip=True)

    content_box = item.find('div', class_='adProduct_etc_box__oL75L')
    avg_rating = review_cnt = None
    if content_box:
        a_tag = content_box.find('a')
        if a_tag:
            avg_rating = a_tag.find('span', class_='adProduct_rating__vk1YN')
            avg_rating = avg_rating.get_text(strip=True) if avg_rating else None

            review_cnt = a_tag.find('em', class_='adProduct_count__J5x57')
            review_cnt = review_cnt.get_text(strip=True) if review_cnt else None

    return kind, rank, is_ad, product_title, product_id, brand, review_cnt, avg_rating, product_url

def parse_super_saving_product(item):
    kind = '슈퍼적립상품'
    title_tag = item.find('div', class_='superSavingProduct_title__WwZ_b')
    product_title = title_tag.get_text(strip=True)

    a_tag = title_tag.find('a')
    rank = a_tag.get('data-shp-contents-rank')
    is_ad = a_tag.get('data-shp-contents-grp')

    product_id = product_url = None
    if a_tag and a_tag.has_attr('data-shp-contents-dtl'):
        shp_data = json.loads(a_tag['data-shp-contents-dtl'])
        for sd in shp_data:
            key = sd.get('key')
            value = sd.get('value')
            if key == 'chnl_prod_no':
                product_id = value
            elif key == 'nv_mid' and product_id is None:
                product_id = value 
            elif key == 'href':
                product_url = value

    if not product_url:
        product_url = a_tag.get('href')

    mall_title_div = item.find('div', class_='superSavingProduct_mall_title__HQ6yD')
    brand = mall_title_div.find('a').get_text(strip=True)

    content_box = item.find('div', class_='superSavingProduct_etc_box__AzCp_')
    avg_rating = review_cnt = None
    if content_box:
        a_tag = content_box.find('a')
        if a_tag:
            avg_rating = a_tag.find('span', class_='superSavingProduct_grade__wRr4y')
            avg_rating = avg_rating.get_text(strip=True) if avg_rating else None

            review_cnt = a_tag.find('em', class_='superSavingProduct_num__cFGGK')
            review_cnt = review_cnt.get_text(strip=True) if review_cnt else None

    return kind, rank, is_ad, product_title, product_id, brand, review_cnt, avg_rating, product_url

def parse_general_product(item):
    kind = '일반상품'
    title_tag = item.find('div', class_='product_title__ljFM_')
    product_title = title_tag.get_text(strip=True)

    a_tag = title_tag.find('a')
    rank = a_tag.get('data-shp-contents-rank')
    is_ad = a_tag.get('data-shp-contents-grp')
    product_id = a_tag.get('data-shp-contents-id')
    product_url = a_tag.get('href')

    mall_title_div = item.find('div', class_='product_mall_title__sJPEp')
    a_tag = mall_title_div.find('a')

    if a_tag:
        a_text = re.sub(r"\s+", " ", a_tag.get_text(strip=True))
        if a_text in ["쇼핑몰별 최저가", "브랜드 카탈로그"]:
            ul = item.find('ul', class_='product_mall_list__rYuBz')
            li = ul.find('li') if ul else None
            brand_span = li.find('span', class_='product_mall_name__DuUQV') if li else None
            brand = brand_span.get_text(strip=True) if brand_span else a_text
        else:
            brand = a_text
    else:
        brand = None

    content_box = item.find('div', class_='product_etc_box__ry70z')
    avg_rating = review_cnt = None
    if content_box:
        a_tag = content_box.find('a')
        if a_tag:
            avg_rating = a_tag.find('span', class_='product_grade__O_5f5')
            avg_rating = avg_rating.get_text(strip=True) if avg_rating else None

            review_cnt = a_tag.find('em', class_='product_num__WuH26')
            review_cnt = review_cnt.get_text(strip=True) if review_cnt else None

    return kind, rank, is_ad, product_title, product_id, brand, review_cnt, avg_rating, product_url

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
    return int(raw)

def parse_rating(raw):
    if pd.isna(raw):
        return None
    match = re.search(r'(\d+\.\d+)', str(raw))
    return float(match.group(1)) if match else None

def process_html_file(file_path: Path, platform_name="네이버가격비교"):
    results = []
    keyword = file_path.stem.strip()
    keyword = unicodedata.normalize("NFC", str(keyword))

    with file_path.open('r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    product_list = soup.find('div', class_='basicList_list_basis__XVx_G')
    if not product_list:
        return results

    top10_items = product_list.find_all(
        'div', class_=[
            'adProduct_item__T7utB',
            'superSavingProduct_item__6mR7_',
            'product_item__KQayS'
        ])[:10]

    for idx, item in enumerate(top10_items, 1):
        item_classes = item.get('class', [])
        if 'adProduct_item__T7utB' in item_classes:
            result = parse_ad_product(item)
        elif 'superSavingProduct_item__6mR7_' in item_classes:
            result = parse_super_saving_product(item)
        elif 'product_item__KQayS' in item_classes:
            result = parse_general_product(item)
        else:
            result = ('구분 불가', None, None, None, None, None, None, None, None)

        kind, rank, is_ad, product_title, product_id, brand, review_cnt, avg_rating, product_url = result

        results.append({
            'keyword': keyword,
            'rank': idx,
            'rank_in_type': rank,
            'product_type': kind,
            'is_ad': is_ad == 'ad',
            'platform': platform_name,
            'brand': brand,
            'product_title': product_title,
            'product_id': product_id,
            'review_cnt': parse_review_count(review_cnt),
            'avg_rating': parse_rating(avg_rating),
            'product_url': product_url
        })

    return results

def process_html_folder(input_folder: Path, output_csv: Path, collected_dt: str):
    all_records = []
    for file in input_folder.glob("*.html"):
        records = process_html_file(file)
        all_records.extend(records)

    df = pd.DataFrame(all_records)
    df['collected_dt'] = pd.to_datetime(collected_dt).date()

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
    input_dir = search_rank_dir / "html" / "price_compare" / f"html_{target_date}"
    output_file = search_rank_dir / "data" / "price_compare" / f"search_rank_{target_date}.csv"

    process_html_folder(input_dir, output_file, collected_dt=target_date)
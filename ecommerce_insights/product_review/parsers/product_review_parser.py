from pathlib import Path
from bs4 import BeautifulSoup
import pandas as pd
import hashlib
import argparse
import json
import re
from datetime import datetime

BRANDS = ["ddakjoa", "sasami80", "gaonnuri", "goldhome"]
BASE_DIR = Path(__file__).resolve().parent.parent

def generate_review_id(brand, product_id, review_dt, author, review_text):
    base = f"{brand}_{product_id}_{review_dt}_{author[:3]}_{review_text[:20]}"
    h = hashlib.md5(base.encode("utf-8")).hexdigest()[:10]
    return f"{brand}_{product_id}_{review_dt.replace('-', '')}_{h}"

def parse_review_html(file_path: Path, brand: str, collected_dt: str):
    product_id = file_path.stem.split("_")[0]

    with file_path.open(encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    review_blocks = soup.find_all("li", class_=re.compile("BnwL_cs1av"))
    rows = []

    for block in review_blocks:
        # 리뷰 작성자
        try:
            review_author = block.find("strong", class_="_2L3vDiadT9").text.strip()
        except:
            review_author = None

        # 리뷰 작성일자
        try:
            review_dt_elem = block.select_one("div.iWGqB6S4Lq span._2L3vDiadT9")
            review_dt = review_dt_elem.text.strip() if review_dt_elem else None
            review_dt_fmt = pd.to_datetime(review_dt.rstrip(".").replace(".", "-"), format="%y-%m-%d").strftime("%Y-%m-%d") if review_dt else None
        except:
            review_dt_fmt = None
        
        # 리뷰 평점
        try:
            review_rating = block.find("em", class_="_15NU42F3kT").text.strip()
        except:
            review_rating = None

        # 리뷰 본문
        try:
            review_text_elem = block.select_one("div._3z6gI4oI6l div._1kMfD5ErZ6 span._2L3vDiadT9")
            review_text = review_text_elem.text.strip() if review_text_elem else ""
        except:
            review_text = ""

        # 사진 여부
        try:
            has_image = True if block.find("img", alt="review_image") else False
        except:
            has_image = False

        # 구매 이력 태그
        try:
            purchase_info_tags = [tag.text.strip() for tag in block.select("div._1kMfD5ErZ6 span.byXA4FP1Bq")]
        except:
            purchase_info_tags = None

        # 구매자 입력 태그
        try:
            tag_items = block.select("div._2FXNMst_ak div._1QLwBCINAr")
            review_tags = [f"{tag.select_one('dt').text.strip()}:{tag.select_one('dd').text.strip()}" for tag in tag_items] if tag_items else None
        except:
            review_tags = None

        # 판매자 답변 내용
        try:
            reply_elem = block.find("div", class_="_5TN6ospbK7")
            reply_text = reply_elem.text.strip() if reply_elem else None
        except:
            reply_text = None

        # 판매자 답변 일자
        try:
            reply_dt_elem = block.select_one("div._3z6gI4oI6l span._3SyGNClj2z")
            reply_dt = reply_dt_elem.text.strip() if reply_dt_elem else None
            reply_dt_fmt = pd.to_datetime(reply_dt.rstrip(".").replace(".", "-"), format="%y-%m-%d").strftime("%Y-%m-%d") if reply_dt else None
        except:
            reply_dt_fmt = None

        # 고유 리뷰 ID
        review_id = generate_review_id(brand, product_id, review_dt_fmt or "", review_author or "", review_text)

        # 결과 저장
        rows.append({
            "product_id": product_id,
            "review_id": review_id,
            "review_author": review_author,
            "review_dt": review_dt_fmt,
            "review_rating": review_rating,
            "review_text": review_text,
            "has_image": has_image,
            "purchase_info_tags": json.dumps(purchase_info_tags, ensure_ascii=False),
            "review_tags": json.dumps(review_tags, ensure_ascii=False),
            "reply_dt": reply_dt_fmt,
            "reply_text": reply_text,
            "platform": "네이버플러스스토어",
            "collected_dt": pd.to_datetime(collected_dt).strftime("%Y-%m-%d")
        })

    return rows

def run_parser(collected_dt: str):
    all_records = []
    for brand in BRANDS:
        html_dir = BASE_DIR / "html" / brand
        for file_path in html_dir.glob("*.html"):
            all_records.extend(parse_review_html(file_path, brand, collected_dt))

    df = pd.DataFrame(all_records)
    df["review_text"] = df["review_text"].replace(r"\s+", " ", regex=True)
    df["reply_text"] = df["reply_text"].replace(r"\s+", " ", regex=True)

    output_file = BASE_DIR / "data" / f"product_review_{collected_dt}.csv"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_file, index=False, encoding="utf-8-sig")
    print(f"[저장 완료] {output_file.as_posix()}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", type=str, required=True, help="수집일자 YYYYMMDD")
    args = parser.parse_args()
    run_parser(args.date)

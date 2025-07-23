from pathlib import Path
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import unicodedata
import argparse
import hashlib

def safe_parse_date(date_str, input_format="%Y-%m-%d", output_format="%Y-%m-%d"):
    date_clean = date_str.rstrip(".").replace(".", "-")
    date_parsed = pd.to_datetime(date_clean, format=input_format, errors='coerce')
    return date_parsed.strftime(output_format) if pd.notnull(date_parsed) else ""

def generate_qna_id(brand, product_id, question_dt, author, question_text):
    base = f"{brand}_{product_id}_{question_dt}_{author[:3]}_{question_text[:20]}"
    h = hashlib.md5(base.encode("utf-8")).hexdigest()[:10]  # 10자리 해시
    return f"{brand}_{product_id}_{question_dt.replace('-', '')}_{h}"

def parse_qna_from_html(file_path: Path, brand_name: str, result_list: list):
    product_id = file_path.stem.split("_")[0]

    with file_path.open(encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
        qna_blocks = soup.find_all("li", class_="bd_1CTeW")

        for block in qna_blocks:
            try:
                question_author = block.find("div", class_="bd_hiIaa").text.strip()
                question_dt = block.find("div", class_="bd_3LGpu").text.strip()
                question_dt_fmt = safe_parse_date(question_dt)

                q_text_elem = block.select_one("div.bd_li1a5 > p.bd_1eMA7")
                question_text = q_text_elem.text.strip() if q_text_elem else ""

                qna_id = generate_qna_id(brand_name, product_id, question_dt_fmt, question_author, question_text)

                is_answered = bool(block.find("div", class_="bd_2gFls"))

                a_text_elem = block.select_one("div.bd_1pL71 > p.bd_1eMA7")
                answer_text = a_text_elem.text.strip() if a_text_elem else ""

                a_dt_elem = block.find("div", class_="bd_1jSWK")
                answer_dt = safe_parse_date(a_dt_elem.text.strip()) if a_dt_elem else ""

                is_secret = 1 if not question_text else 0

                result_list.append({
                    "product_id": product_id,
                    "qna_id": qna_id,
                    "question_author": question_author,
                    "question_dt": question_dt_fmt,
                    "question_text": question_text,
                    "is_answered": is_answered,
                    "answer_text": answer_text,
                    "answer_dt": answer_dt,
                    "is_secret": is_secret,
                    "platform": "네이버플러스스토어",
                    "collected_dt": datetime.today().strftime("%Y-%m-%d")
                })

            except Exception as e:
                print(f"[에러] {file_path}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", type=str, help="저장 파일명에 포함될 날짜 (예: 20250624)", default=datetime.today().strftime("%Y%m%d"))
    args = parser.parse_args()

    base_dir = Path(__file__).resolve().parent.parent
    brand_dirs = ["ddakjoa", "sasami80", "gaonnuri", "goldhome"]
    output_path = base_dir / "data" / f"product_qna_{args.date}.csv"

    all_qna = []

    for brand in brand_dirs:
        brand_path = base_dir / "html" / brand
        for html_file in brand_path.glob("*.html"):
            parse_qna_from_html(html_file, brand, all_qna)

    df = pd.DataFrame(all_qna)
    df["question_text"] = df["question_text"].replace(r"\s+", " ", regex=True)
    df["answer_text"] = df["answer_text"].replace(r"\s+", " ", regex=True)

    # 중복 제거: qna_id 기준 (html 중복 저장 방지 목적)
    df.drop_duplicates(subset=["qna_id"], inplace=True)

    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"[저장 완료] {output_path.as_posix()} ({len(df)}건)")

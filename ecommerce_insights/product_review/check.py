from google.cloud import bigquery
from google.oauth2 import service_account
from datetime import datetime
from pathlib import Path
import argparse

# 인증 및 BQ 클라이언트 설정
BASE_DIR = Path(__file__).resolve().parent.parent.parent
CREDENTIALS_FILE = str((BASE_DIR / "manggu-e08c8cf179d0.json").as_posix())
credentials = service_account.Credentials.from_service_account_file(CREDENTIALS_FILE)
client = bigquery.Client(credentials=credentials, project=credentials.project_id)

# 테이블 정보
project_id = "manggu"
dataset_id = "ecommerce_insights"
table_id = "product_review"
table_ref = f"{project_id}.{dataset_id}.{table_id}"

def run_query(query):
    return list(client.query(query).result())

def check_review_duplicates(target_date: str):
    print(f"\n📋 product_review 정합성 체크 시작: {target_date}")

    # 1. 수집일 기준 전체 건수
    total = run_query(f"""
        SELECT COUNT(*) AS cnt
        FROM `{table_ref}`
        WHERE collected_dt = PARSE_DATE('%Y%m%d', '{target_date}')
    """)[0].cnt
    print(f"✅ 수집일 기준 총 건수: {total}건")

    # 2. review_id 기준 중복 체크
    dup_result = run_query(f"""
        SELECT COUNT(*) AS dup_cnt FROM (
            SELECT review_id, COUNT(*)
            FROM `{table_ref}`
            WHERE collected_dt = PARSE_DATE('%Y%m%d', '{target_date}')
            GROUP BY review_id
            HAVING COUNT(*) > 1
        )
    """)[0].dup_cnt

    if dup_result > 0:
        print(f"⚠️ 중복된 review_id가 {dup_result}건 존재합니다.")
    else:
        print("✅ review_id 기준 중복 없음")

    # 3. 논리적 중복 체크 (product_id + review_author + review_dt + review_text)
    similar_result = run_query(f"""
        SELECT COUNT(*) AS dup_cnt FROM (
            SELECT product_id, review_author, review_dt, review_text, COUNT(*)
            FROM `{table_ref}`
            WHERE collected_dt = PARSE_DATE('%Y%m%d', '{target_date}')
            GROUP BY product_id, review_author, review_dt, review_text
            HAVING COUNT(*) > 1
        )
    """)[0].dup_cnt

    if similar_result > 0:
        print(f"⚠️ 동일 product_id + review_author + review_dt + review_text 중복 {similar_result}건 존재")
    else:
        print("✅ 리뷰 텍스트 기준 논리적 중복 없음")

    # 4. 브랜드/제품별 리뷰 수 + 날짜 범위
    print("\n📊 브랜드/제품별 리뷰 건수 및 작성일자 분포:")

    records = run_query(f"""
        SELECT
            REGEXP_EXTRACT(review_id, r'^([a-z0-9]+)') AS brand,
            product_id,
            COUNT(*) AS review_count,
            MIN(review_dt) AS min_dt,
            MAX(review_dt) AS max_dt
        FROM `{table_ref}`
        WHERE collected_dt = PARSE_DATE('%Y%m%d', '{target_date}')
        GROUP BY brand, product_id
        ORDER BY brand, product_id
    """)

    for row in records:
        print(f"  - [{row.brand}] {row.product_id} : {row.review_count}건 ({row.min_dt} ~ {row.max_dt})")

    print("\n✅ 정합성 체크 완료")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", type=str, required=True, help="YYYYMMDD 형식 수집일자")
    args = parser.parse_args()
    check_review_duplicates(args.date)

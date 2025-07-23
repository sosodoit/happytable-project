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
table_id = "product_qna"

table_ref = f"{project_id}.{dataset_id}.{table_id}"

def run_query(query):
    return list(client.query(query).result())

def check_qna_duplicates(target_date: str):
    print(f"\nproduct_qna 중복 정합성 체크: {target_date}")

    # 수집일 기준 전체 건수
    total = run_query(f"""
        SELECT COUNT(*) AS cnt
        FROM `{table_ref}`
        WHERE collected_dt = PARSE_DATE('%Y%m%d', '{target_date}')
    """)[0].cnt
    print(f"✅ 수집일 기준 총 건수: {total}건")

    # qna_id 기준 중복 체크
    dup_result = run_query(f"""
        SELECT COUNT(*) AS dup_cnt FROM (
            SELECT qna_id, COUNT(*)
            FROM `{table_ref}`
            WHERE collected_dt = PARSE_DATE('%Y%m%d', '{target_date}')
            GROUP BY qna_id
            HAVING COUNT(*) > 1
        )
    """)[0].dup_cnt

    if dup_result > 0:
        print(f"⚠️ 중복된 qna_id가 {dup_result}건 존재합니다.")
    else:
        print("✅ qna_id 기준 중복 없음")

    # 동일 product_id + question_author + question_dt + question_text 조합 중복 체크
    similar_result = run_query(f"""
        SELECT COUNT(*) AS dup_cnt FROM (
            SELECT product_id, question_author, question_dt, question_text, COUNT(*)
            FROM `{table_ref}`
            WHERE collected_dt = PARSE_DATE('%Y%m%d', '{target_date}')
            GROUP BY product_id, question_author, question_dt, question_text
            HAVING COUNT(*) > 1
        )
    """)[0].dup_cnt

    if similar_result > 0:
        print(f"⚠️ 동일 product_id + question_author + question_dt + question_text 중복 {similar_result}건 존재")
    else:
        print("✅ 질문 텍스트 기준 논리적 중복 없음")

    print("\n✅ 정합성 체크 완료")

    # 브랜드/제품별 Q&A 개수 및 질문일자 범위 확인
    print("\n📊 브랜드/제품별 Q&A 건수 및 질문일자 분포:")

    records = run_query(f"""
        SELECT
        REGEXP_EXTRACT(qna_id, r'^([a-z0-9]+)') AS brand,
        product_id,
        COUNT(*) AS qna_count,
        MIN(question_dt) AS min_dt,
        MAX(question_dt) AS max_dt
        FROM `{table_ref}`
        WHERE collected_dt = PARSE_DATE('%Y%m%d', '{target_date}')
        GROUP BY brand, product_id
        ORDER BY brand, product_id
    """)

    for row in records:
        print(f"  - [{row.brand}] {row.product_id} : {row.qna_count}건 ({row.min_dt} ~ {row.max_dt})")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", type=str, required=True, help="YYYYMMDD 형식 수집일자")
    args = parser.parse_args()

    check_qna_duplicates(args.date)

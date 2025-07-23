from google.cloud import bigquery
from google.oauth2 import service_account
from datetime import datetime
from pathlib import Path

# 인증 및 BQ 클라이언트 설정
BASE_DIR = Path(__file__).resolve().parent.parent.parent
CREDENTIALS_FILE = str((BASE_DIR / "manggu-e08c8cf179d0.json").as_posix())
credentials = service_account.Credentials.from_service_account_file(CREDENTIALS_FILE)
client = bigquery.Client(credentials=credentials, project=credentials.project_id)

# 테이블 정보
project_id = "manggu"
dataset_id = "ecommerce_insights"
table_id = "search_rank"

table_ref = f"{project_id}.{dataset_id}.{table_id}"

def run_query(sql):
    return list(client.query(sql).result())

def check_search_rank(target_date: str):
    print(f"\n정합성 체크 시작: {target_date}")

    # 1. 해당 날짜 건수 확인
    total_rows = run_query(f"""
        SELECT COUNT(*) AS cnt
        FROM `{table_ref}`
        WHERE collected_dt = PARSE_DATE('%Y%m%d', '{target_date}')
    """)[0].cnt
    print(f"✅ 총 {total_rows}건 수집됨")

    # 2. 필수 컬럼 NULL 여부
    nulls = run_query(f"""
        SELECT
          COUNTIF(keyword IS NULL) AS null_keyword,
          COUNTIF(rank IS NULL) AS null_rank,
          COUNTIF(product_id IS NULL) AS null_pid,
          COUNTIF(collected_dt IS NULL) AS null_date
        FROM `{table_ref}`
        WHERE collected_dt = PARSE_DATE('%Y%m%d', '{target_date}')
    """)[0]

    if nulls.null_keyword or nulls.null_rank or nulls.null_pid or nulls.null_date:
        print("⚠️ NULL 항목 존재:")
        print(f"   - keyword NULL: {nulls.null_keyword}")
        print(f"   - rank NULL: {nulls.null_rank}")
        print(f"   - product_id NULL: {nulls.null_pid}")
        print(f"   - collected_dt NULL: {nulls.null_date}")
    else:
        print("✅ 필수 컬럼 NULL 없음")

    # 3. 중복 체크 (keyword + rank + platform + collected_dt 기준)
    dup = run_query(f"""
        SELECT COUNT(*) AS dup_cnt FROM (
          SELECT keyword, rank, platform, collected_dt, COUNT(*)
          FROM `{table_ref}`
          WHERE collected_dt = PARSE_DATE('%Y%m%d', '{target_date}')
          GROUP BY keyword, rank, platform, collected_dt
          HAVING COUNT(*) > 1
        )
    """)[0].dup_cnt

    if dup > 0:
        print(f"⚠️ 중복 데이터 존재: {dup}건")
    else:
        print("✅ keyword + rank + platform + collected_dt 기준 중복 없음")

    # 4. 플랫폼별 분포 확인
    rows = run_query(f"""
        SELECT platform, COUNT(*) AS cnt
        FROM `{table_ref}`
        WHERE collected_dt = PARSE_DATE('%Y%m%d', '{target_date}')
        GROUP BY platform
        ORDER BY cnt DESC
    """)
    print("📊 플랫폼별 분포:")
    for row in rows:
        print(f"   - {row.platform}: {row.cnt}건")

    print("\n✅ 정합성 체크 완료")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", type=str, help="YYYYMMDD 형식 날짜", default=datetime.today().strftime("%Y%m%d"))
    args = parser.parse_args()

    check_search_rank(args.date)
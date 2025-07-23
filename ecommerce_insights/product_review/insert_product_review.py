import pandas as pd
import argparse
from google.oauth2 import service_account
from google.cloud import bigquery
import pandas_gbq
from pathlib import Path

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
product_review_dir = Path(__file__).resolve().parent

# 기존 테이블 비우기 (TRUNCATE)
truncate_query = f"TRUNCATE TABLE `{table_ref}`"
client.query(truncate_query).result()
print(f"[INFO] {table_id} 테이블 비움 완료.")

def upload_review(target_date: str):
    csv_path = product_review_dir / "data" / f"product_review_{target_date}.csv"
    if not csv_path.exists():
        print(f"❌ 파일 없음: {csv_path}")
        return

    print(f"CSV 로딩: {csv_path.name}")
    dtype_spec = {
        "product_id":'string',
        "review_id":'string',
        "review_author":'string',
        "review_rating":'float64',
        "review_text":'string',
        "has_image":'boolean',
        "purchase_info_tags":'string',
        "review_tags":'string',
        "reply_text":'string',
        "platform":'string'
    }

    df = pd.read_csv(csv_path, dtype=dtype_spec, parse_dates=["review_dt", "reply_dt", "collected_dt"])

    # 중복 제거
    before = len(df)
    df.drop_duplicates(subset=["review_id"], inplace=True)
    after = len(df)
    print(f"🧹 중복 제거: {before - after}건 제거됨 ({after}건 유지)")

    # 업로드
    pandas_gbq.to_gbq(
        df,
        destination_table=table_ref,
        project_id=project_id,
        if_exists="append",
        credentials=credentials
    )

    print(f"✅ 업로드 완료: {table_ref} ({after}건)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", type=str, required=True, help="CSV 저장 날짜 (예: 20250624)")
    args = parser.parse_args()

    upload_review(args.date)

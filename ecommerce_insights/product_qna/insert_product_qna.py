from pathlib import Path
import pandas as pd
import argparse
from google.oauth2 import service_account
import pandas_gbq
from google.cloud import bigquery

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
product_qna_dir = Path(__file__).resolve().parent

# 기존 테이블 비우기 (TRUNCATE)
truncate_query = f"TRUNCATE TABLE `{project_id}.{dataset_id}.{table_id}`"
client.query(truncate_query).result()
print(f"[INFO] {table_id} 테이블 비움 완료.")

def upload_qna(target_date: str):
    csv_path = product_qna_dir / "data" / f"product_qna_{target_date}.csv"
    if not csv_path.exists():
        print(f"❌ 파일 없음: {csv_path}")
        return

    print(f"CSV 로딩: {csv_path.name}")
    dtype_spec = {
        "product_id": 'string',
        "qna_id": 'string',
        "question_author": 'string',
        "question_text": 'string',
        "is_answered": 'boolean',
        "answer_text": 'string',
        "is_secret": 'Int64',
        "platform": 'string'
    }

    df = pd.read_csv(csv_path, dtype=dtype_spec, parse_dates=["question_dt", "answer_dt", "collected_dt"])

    # 업로드 전에 중복 제거: qna_id 기준
    before = len(df)
    df.drop_duplicates(subset=["qna_id"], inplace=True)
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

    upload_qna(args.date)

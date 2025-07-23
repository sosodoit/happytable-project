import pandas as pd
from datetime import datetime
from google.cloud import bigquery
from google.oauth2 import service_account
import pandas_gbq
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
table_id = "search_rank"
search_rank_dir = Path(__file__).resolve().parent

def upload_search_rank(channel: str, target_date: str):
    # 경로 설정
    if channel == "price_compare":
        csv_path = search_rank_dir / "data" / "price_compare" / f"search_rank_{target_date}.csv"
    elif channel == "smartstore":
        csv_path = search_rank_dir / "data" / "smartstore" / f"search_rank_nss_{target_date}.csv"
    else:
        raise ValueError("채널은 'price_compare' 또는 'smartstore' 중 하나여야 합니다.")

    if not csv_path.exists():
        print(f"[스킵] 파일 없음: {csv_path}")
        return

    # 데이터 로드
    dtype_spec = {
        'rank': 'Int64',
        'product_id': 'string',
        'review_cnt': 'Int64',
        'avg_rating': 'float64'
    }
    df = pd.read_csv(csv_path, dtype=dtype_spec, parse_dates=['collected_dt'])

    # 중복 제거: 동일 product_id + collected_dt만 남기기 (필요시 정제 기준 확장 가능)
    df.drop_duplicates(subset=['product_id', 'collected_dt'], inplace=True)

    # BigQuery 업로드
    pandas_gbq.to_gbq(
        df,
        destination_table=f"{project_id}.{dataset_id}.{table_id}",
        project_id="manggu",
        if_exists="append",
        credentials=credentials
    )
    print(f"[INFO] {len(df)}건 업로드 완료.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--channel", type=str, choices=["price_compare", "smartstore"], required=True, help="채널명: price_compare or smartstore")
    parser.add_argument("--date", type=str, help="수집 대상 날짜 (YYYYMMDD)", default=datetime.today().strftime("%Y%m%d"))
    args = parser.parse_args()

    upload_search_rank(channel=args.channel, target_date=args.date)

import pandas as pd
from datetime import datetime
from google.cloud import bigquery
from google.oauth2 import service_account
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
table_id = "product_info_daily"

# 1. 기존 테이블 비우기 (TRUNCATE)
truncate_query = f"TRUNCATE TABLE `{project_id}.{dataset_id}.{table_id}`"
client.query(truncate_query).result()
print(f"[INFO] {table_id} 테이블 비움 완료.")

# 2. CSV 로드
dtype_spec = {
    "product_id":'string',
    "product_title":'string',
    "brand":'string',
    "list_price":'Int64',
    "discount_price":'Int64',
    "sales_status":'string',
    "avg_rating":'float64',
    "review_cnt":'Int64',
    "platform":'string'
}

CSV_FILE = str((Path(__file__).resolve().parent / "product_info_daily.csv").as_posix())
df = pd.read_csv(CSV_FILE, dtype=dtype_spec, parse_dates=["collected_dt"])
df = df.loc[:, ~df.columns.str.contains("^Unnamed")]  # Unnamed 컬럼 제거

# 3. BigQuery 적재
pandas_gbq.to_gbq(
    df,
    destination_table=f"{project_id}.{dataset_id}.{table_id}",
    project_id="manggu",
    if_exists="append",
    credentials=credentials
)

print(f"[INFO] {len(df)}건 업로드 완료.")
from google.cloud import bigquery
from google.oauth2 import service_account
from pathlib import Path

# 인증 및 BQ 클라이언트 설정
BASE_DIR = Path(__file__).resolve().parent.parent.parent
CREDENTIALS_FILE = str((BASE_DIR / "manggu-e08c8cf179d0.json").as_posix())
# CREDENTIALS_FILE = "../../manggu-e08c8cf179d0.json" 
credentials = service_account.Credentials.from_service_account_file(CREDENTIALS_FILE)
client = bigquery.Client(credentials=credentials, project=credentials.project_id)

# 테이블 정보
project_id = "manggu"
dataset_id = "ecommerce_insights"
table_id = "product_info"

table_ref = f"{project_id}.{dataset_id}.{table_id}"

def run_query(query):
    return client.query(query).result()

# 전체 통과 여부 플래그
integrity_passed = True  

# 1. 전체 건수
total_rows = list(run_query(f"SELECT COUNT(*) AS cnt FROM `{table_ref}`"))[0].cnt
print(f"✅ 총 {total_rows}건이 적재되어 있습니다.")

# 2. product_id NULL 확인
null_product_id = list(run_query(f"""
    SELECT COUNT(*) AS cnt
    FROM `{table_ref}`
    WHERE product_id IS NULL
"""))[0].cnt
if null_product_id > 0:
    print(f"⚠️ product_id가 NULL인 행이 {null_product_id}건 존재합니다.")
    integrity_passed = False
else:
    print("✅ product_id NULL 없음")

# 3. product_id 중복 확인
duplicate_product_id = list(run_query(f"""
    SELECT COUNT(*) AS cnt FROM (
        SELECT product_id
        FROM `{table_ref}`
        GROUP BY product_id
        HAVING COUNT(*) > 1
    )
"""))[0].cnt
if duplicate_product_id > 0:
    print(f"⚠️ 중복된 product_id가 {duplicate_product_id}건 존재합니다.")
    integrity_passed = False
else:
    print("✅ product_id 중복 없음")

# 4. 수집/수정일자 최신 확인
recent_date = list(run_query(f"""
    SELECT MAX(collected_dt) AS max_dt
    FROM `{table_ref}`
"""))[0].max_dt
print(f"📅 가장 최근 수정일: {recent_date}")

# 5. 플랫폼 NULL 또는 공백 확인
platform_nulls = list(run_query(f"""
    SELECT COUNT(*) AS cnt
    FROM `{table_ref}`
    WHERE platform IS NULL OR TRIM(platform) = ''
"""))[0].cnt
if platform_nulls > 0:
    print(f"⚠️ platform 누락(또는 공백) {platform_nulls}건 존재")
    integrity_passed = False
else:
    print("✅ platform 입력값 정상")

# 6. 주요 컬럼 Null 비율
row = list(run_query(f"""
    SELECT
      COUNTIF(brand IS NULL) AS brand_nulls,
      COUNTIF(seller IS NULL) AS seller_nulls,
      COUNTIF(product_url IS NULL) AS url_nulls
    FROM `{table_ref}`
"""))[0]

print(f"📌 brand NULL: {row.brand_nulls}, seller NULL: {row.seller_nulls}, product_url NULL: {row.url_nulls}")

# 완료 로그
if integrity_passed:
    print("\n✅ 모든 항목 통과: product_info_daily 정합성 체크 완료")
else:
    print("\n❌ 정합성 체크 실패: 위 항목 중 하나 이상에서 문제가 발생했습니다.")

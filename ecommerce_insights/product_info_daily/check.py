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
table_id = "product_info_daily"

table_ref = f"{project_id}.{dataset_id}.{table_id}"

def run_query(query):
    return client.query(query).result()

# 전체 통과 여부 플래그
integrity_passed = True  

# 1. 전체 건수
total_rows = list(run_query(f"SELECT COUNT(*) AS cnt FROM `{table_ref}`"))[0].cnt
print(f"✅ 총 {total_rows}건이 적재되어 있습니다.")

# 2. 필수 컬럼 NULL 확인
row = list(run_query(f"""
    SELECT
      COUNTIF(product_id IS NULL) AS null_product_id,
      COUNTIF(collected_dt IS NULL) AS null_date,
      COUNTIF(discount_price IS NULL) AS null_discount,
      COUNTIF(platform IS NULL OR TRIM(platform) = '') AS null_platform
    FROM `{table_ref}`
"""))[0]

if row.null_product_id > 0:
    print(f"⚠️ product_id NULL: {row.null_product_id}건")
    integrity_passed = False
else:
    print("✅ product_id NULL 없음")

if row.null_date > 0:
    print(f"⚠️ collected_dt NULL: {row.null_date}건")
    integrity_passed = False
else:
    print("✅ 수집일자(collected_dt) NULL 없음")

if row.null_discount > 0:
    print(f"⚠️ discount_price NULL: {row.null_discount}건")
    integrity_passed = False
else:
    print("✅ discount_price 정상 입력")

if row.null_platform > 0:
    print(f"⚠️ platform 누락: {row.null_platform}건")
    integrity_passed = False
else:
    print("✅ platform 입력값 정상")

# 3. product_id + collected_dt 중복 확인
dup_count = list(run_query(f"""
    SELECT COUNT(*) AS cnt FROM (
      SELECT product_id, collected_dt
      FROM `{table_ref}`
      GROUP BY product_id, collected_dt
      HAVING COUNT(*) > 1
    )
"""))[0].cnt

if dup_count > 0:
    print(f"⚠️ product_id + collected_dt 중복: {dup_count}건")
    integrity_passed = False
else:
    print("✅ product_id + collected_dt 유일성 확보됨")

# 4. 수집일자별 분포 확인 (최신 수집일자 기준 최근 7일)
latest_date = list(run_query(f"""
    SELECT MAX(collected_dt) AS max_dt
    FROM `{table_ref}`
"""))[0].max_dt

print(f"\n📅 수집 기준일: {latest_date} 기준 최근 7일 분포:")

results = run_query(f"""
    SELECT collected_dt, COUNT(*) AS cnt
    FROM `{table_ref}`
    WHERE collected_dt BETWEEN DATE_SUB(DATE('{latest_date}'), INTERVAL 6 DAY) AND DATE('{latest_date}')
    GROUP BY collected_dt
    ORDER BY collected_dt DESC
""")

for row in results:
    print(f"  - {row.collected_dt}: {row.cnt}건")

# 5. 가격 이상치 확인 (정가 < 할인가)
invalid_price = list(run_query(f"""
    SELECT COUNT(*) AS cnt
    FROM `{table_ref}`
    WHERE list_price IS NOT NULL
      AND discount_price IS NOT NULL
      AND list_price < discount_price
"""))[0].cnt

if invalid_price > 0:
    print(f"⚠️ 정가 < 할인가 이상치: {invalid_price}건")
    integrity_passed = False
else:
    print("✅ 정가 ≤ 할인가 이상 없음")

# 완료 로그
if integrity_passed:
    print("\n✅ 모든 항목 통과: product_info_daily 정합성 체크 완료")
else:
    print("\n❌ 정합성 체크 실패: 위 항목 중 하나 이상에서 문제가 발생했습니다.")


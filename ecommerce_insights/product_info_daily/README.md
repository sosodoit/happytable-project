# product_info_daily

제품 일일 트래킹 정보를 관리하는 테이블입니다.

## 데이터 흐름
1. `product_info_daily.csv` 생성 또는 갱신
2. `insert_product_info_daily.py` 실행 → 기존 데이터 삭제 후 새로 업로드

## CSV 파일 위치
- `./product_info_daily.csv`

## 테이블 관리 방식
- 덮어쓰기 (TRUNCATE → append)
- product_id + collected_dt 조합 기준으로 유일성 유지

## 실행 방법
```bash
python insert_product_info_daily.py
```

## 주의 사항
- `product_id`, `collected_dt`는 **NOT NULL**이어야 하며, 누락 시 정합성 오류 발생
- `product_id + collected_dt` 조합은 **논리적 유니크 키**로, 중복 데이터가 있으면 분석 및 집계 결과에 오류 발생 가능
- `list_price < discount_price`인 경우는 **이상치**로 간주되어 검증 대상
- CSV 파일 컬럼 순서와 이름은 테이블 스키마와 **정확히 일치**해야 함
- 테이블 업로드 시 기존 데이터를 TRUNCATE(초기화) 후 append 하므로, **전체 데이터가 매번 포함되어야 함**
- CSV 파일이 최신 수집 데이터를 반영하고 있는지 사전에 확인 필수
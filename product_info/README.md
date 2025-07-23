# product_info

제품 메타정보를 관리하는 테이블입니다.

## 데이터 흐름
1. `product_info.csv` 갱신
2. `insert_product_info.py` 실행 → 기존 데이터 삭제 후 새로 업로드

## CSV 파일 위치
- `./product_info.csv`

## 테이블 관리 방식
- 덮어쓰기 (TRUNCATE → append)
- collected_dt: 업로드 일자 자동 추가

## 실행 방법
```bash
python insert_product_info.py
```

## 주의 사항
- product_id 기준 유니크
- CSV 컬럼명 변경 시 스키마 오류 주의
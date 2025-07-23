# product_review

브랜드별 네이버 스마트스토어 상품의 리뷰 정보를 수집하여 저장하는 테이블입니다.  
각 제품의 리뷰 및 답변 내역을 HTML로 수집 후 파싱하여 BigQuery에 적재합니다.

## 데이터 흐름

HTML로 저장된 각 브랜드의 제품 리뷰 페이지를 파싱하여 BigQuery에 적재하는 작업 흐름입니다.

1. 브랜드별 HTML 저장 (`product_review/html/{브랜드}/`)
2. `parsers/parse_product_review.py` 실행 → 파싱 결과 CSV 생성 (`data/`)
    ```bash
    python parsers/parse_product_review.py --date YYYYMMDD
    ```
3. `insert/upload_product_review.py` 실행 → 중복 제거 후 BigQuery에 append 적재
    ```bash
    python insert/upload_product_review.py --date YYYYMMDD
    ```
4. **정합성 체크**
    ```bash
    python insert/check_product_review.py --date YYYYMMDD
    ```

## 테이블 관리 방식
- 수집 주기: 비정기 (HTML 수집 시점 기준)
- 적재 방식: TRUNCATE 후 append
- 유일성 기준: `review_id` (작성자 + 리뷰일자 + 리뷰내용 기반 해시)
- 중복 예방: `review_id` 기준 `drop_duplicates()` 사전 처리

## 주의 사항
- 동일 HTML이 여러 번 저장될 수 있으므로, `review_id` 기준 중복 제거 필수
- `review_tags`, `purchase_info_tags`는 리스트 → JSON 문자열로 저장됨
- 날짜 컬럼 (`review_dt`, `reply_dt`, `collected_dt`)은 `DATE` 타입으로 변환 필요
- 브랜드명 폴더는 `ddakjoa`, `sasami80`, `gaonnuri`, `goldhome` 기준
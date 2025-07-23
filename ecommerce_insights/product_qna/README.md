# product_qna

브랜드별 네이버 스마트스토어 상품의 Q&A 정보를 수집하여 저장하는 테이블입니다.  
각 제품의 질문/답변 내역을 HTML로 수집 후 파싱하여 BigQuery에 적재합니다.

## 데이터 흐름

HTML로 저장된 각 브랜드의 제품 Q&A 페이지를 파싱하여 BigQuery에 적재하는 작업 흐름입니다.

1. 브랜드별 HTML 저장 (`product_qna/html/{브랜드}/`)
2. `parsers/product_qna_parse.py` 실행 → 파싱 결과 CSV 생성 (`data/`)
    ```bash
    python parsers/product_qna_parse.py --date YYYYMMDD
    ```
3. `insert_product_qna.py` 실행 → 중복 제거 후 BigQuery에 append 적재
    ```bash
    python insert_product_qna.py --date YYYYMMDD
    ```
4. **정합성 체크**
    ```bash
    python check.py --date YYYYMMDD
    ```

## 테이블 관리 방식
- 수집 주기: 비정기 (HTML 수집 시점 기준)
- 적재 방식: TRUNCATE 후 append
- 유일성 기준: `qna_id` (작성자 + 질문일자 + 질문내용 기반 해시)
- 중복 예방: `qna_id` 기준 `drop_duplicates()` 사전 처리

## 주의 사항
- 동일 HTML이 여러 번 저장될 수 있으므로, `qna_id` 기준 중복 제거 필수
- `question_text`가 비공개인 경우 `is_secret` = 1로 저장됨
- 브랜드명 폴더는 `ddakjoa`, `sasami80`, `gaonnuri`, `goldhome` 기준
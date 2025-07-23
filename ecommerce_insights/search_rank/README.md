# search_rank

네이버 쇼핑의 키워드 검색 결과에서 상위 10개 상품 정보를 수집하여 저장하는 테이블입니다.  
가격비교 영역과 스마트스토어 영역 모두 통합 관리합니다.

## 데이터 흐름

네이버 쇼핑 검색결과를 HTML로 저장 후 파싱하여 BigQuery에 적재하는 작업 흐름입니다.

1. `keywords/keyword_list.txt` 에 검색 키워드 등록
2. `utils/generate_*.py` 실행 → html 파일 생성
3. 크롬 개발자도구(F12) → HTML 저장 (`html/*/html_YYYYMMDD/`)
4. `parsers/*_parser.py` 실행 → 파싱 결과 CSV 생성 (`data/`)

    ```bash
    #가격비교 
    python parsers/price_compare_parser.py --date YYYYMMDD
    
    #스마트스토어
    python parsers/smartstore_parser.py --date YYYYMMDD
    ```

5. `upload_to_bigquery.py` 실행 → BigQuery 적재

    ```bash
    python insert_search_rank.py --channel [price_compare|smartstore] --date YYYYMMDD
    ```

6. **정합성 체크**
    ```bash
    python check.py --date YYYYMMDD
    ```

## 테이블 관리 방식
- 신규 수집일 기준 파싱된 데이터 append
- 유일성 기준: `keyword + rank + platform + collected_dt` 조합
- 데이터 원천: HTML → 파싱 → CSV → BigQuery 적재

## 주의 사항
- 키워드 목록은 `keywords/keyword_list.txt`에서 관리
- 광고상품, 슈퍼적립상품, 일반상품 3종만 파싱 대상
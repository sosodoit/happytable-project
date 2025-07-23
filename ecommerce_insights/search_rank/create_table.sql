CREATE TABLE IF NOT EXISTS `manggu.ecommerce_insights.search_rank` (
  keyword STRING NOT NULL,           -- 검색 키워드
  rank INT64 NOT NULL,               -- 순위 (1~10)
  is_ad BOOL,                        -- 광고 여부 (True/False)
  platform STRING,                   -- 플랫폼명 (네이버가격비교 / 네이버플러스스토어)
  brand STRING,                      -- 브랜드명 또는 판매자명
  product_title STRING,              -- 상품 제목
  product_id STRING,                 -- 상품 고유 식별자 (chnl_prod_no 기준)
  review_cnt INT64,                  -- 리뷰 수
  avg_rating FLOAT64,                -- 평균 평점
  product_url STRING,                -- 상세 페이지 URL
  collected_dt DATE NOT NULL         -- 수집일자 (YYYY-MM-DD)
)
PARTITION BY DATE(collected_dt)
OPTIONS(
  description = "네이버 쇼핑 기반 키워드별 상위 상품 검색 순위 데이터. 광고상품, 슈퍼적립상품, 일반상품 및 스마트스토어 상품 포함."
);

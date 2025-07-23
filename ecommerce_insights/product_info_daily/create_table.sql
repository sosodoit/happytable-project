CREATE TABLE IF NOT EXISTS `manggu.ecommerce_insights.product_info_daily` (
  product_id STRING NOT NULL,           -- 제품 고유 ID
  product_title STRING,                 -- 제품명
  brand STRING,                         -- 브랜드
  list_price INT64,                     -- 정가
  discount_price INT64,                 -- 할인가
  sales_status STRING,                  -- 판매 상태 (예: 판매중, 품절 등)
  avg_rating FLOAT64,                   -- 평균 평점
  review_cnt INT64,                     -- 리뷰 수
  platform STRING,                      -- 쇼핑몰 플랫폼 (네이버, 쿠팡 등)
  collected_dt DATE NOT NULL            -- 수집일자 (일일 적재 기준)
);

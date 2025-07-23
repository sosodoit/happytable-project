CREATE TABLE IF NOT EXISTS `manggu.ecommerce_insights.product_info` (
  product_id STRING NOT NULL,                -- 제품 고유 ID
  product_variants STRING,                   -- 규격/옵션 정보
  brand STRING,                              -- 브랜드명
  manufacturer STRING,                       -- 제조사
  seller STRING,                             -- 판매자명
  product_url STRING,                        -- 상세페이지 URL
  platform STRING,                           -- 쇼핑몰 플랫폼명 (네이버, 쿠팡 등)
  collected_dt DATE                          -- 수집일자 (업로드 시점 기준)
);

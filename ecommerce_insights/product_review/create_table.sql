CREATE TABLE IF NOT EXISTS `manggu.ecommerce_insights.product_review` (
  product_id STRING NOT NULL,             -- 제품 고유 ID
  review_id STRING NOT NULL,              -- 리뷰 고유 ID (해시 기반)
  review_author STRING,                   -- 리뷰 작성자
  review_dt DATE,                         -- 리뷰 작성일
  review_rating FLOAT64,                  -- 리뷰 평점
  review_text STRING,                     -- 리뷰 내용
  has_image BOOL,                         -- 이미지 포함 여부
  purchase_info_tags STRING,              -- 구매 이력 태그 (JSON string)
  review_tags STRING,                     -- 구매자 입력 태그 (JSON string)
  reply_dt DATE,                          -- 판매자 답변일자
  reply_text STRING,                      -- 판매자 답변 내용
  platform STRING,                        -- 수집 플랫폼 (네이버플러스스토어)
  collected_dt DATE                       -- 수집일자
)
PARTITION BY DATE(collected_dt)
OPTIONS (
  description = "브랜드별 네이버 스마트스토어 상품 리뷰 정보. review_id는 리뷰일자 + 작성자 + 텍스트 기반 해시로 생성됨."
);

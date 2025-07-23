CREATE TABLE IF NOT EXISTS `manggu.ecommerce_insights.product_qna` (
  product_id STRING NOT NULL,         -- 제품 고유 ID
  qna_id STRING NOT NULL,             -- Q&A 고유 ID (해시 기반)
  question_author STRING,             -- 질문 작성자 (닉네임 또는 일부 마스킹)
  question_dt DATE,                   -- 질문 작성일자
  question_text STRING,               -- 질문 내용
  is_answered BOOL,                   -- 답변 여부
  answer_text STRING,                 -- 답변 내용
  answer_dt DATE,                     -- 답변 작성일자
  is_secret INT64,                    -- 비공개 여부 (텍스트 없을 경우 1)
  platform STRING,                    -- 플랫폼명 (ex. 네이버플러스스토어)
  collected_dt DATE                   -- 수집일자
)
PARTITION BY DATE(collected_dt)
OPTIONS(
  description = "브랜드별 네이버 스마트스토어 제품의 Q&A 정보. qna_id는 질문일자 + 작성자 + 텍스트 기반 해시로 생성됨."
);

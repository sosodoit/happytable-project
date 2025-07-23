from pathlib import Path
from datetime import datetime

# === 설정 ===
today = datetime.today().strftime("%Y%m%d")
search_rank_dir = Path(__file__).resolve().parent.parent
html_dir = search_rank_dir / "html" / "price_compare"
output_folder = html_dir / f"html_{today}"
keyword_path = search_rank_dir / "keywords" / "keyword_list.txt"

# === 키워드 불러오기 ===
with keyword_path.open(encoding="utf-8") as f:
    keywords = [line.strip() for line in f if line.strip()]

# === 디렉토리 생성 ===
output_folder.mkdir(parents=True, exist_ok=True)

# === 빈 HTML 파일 생성 ===
for keyword in keywords:
    file_name = f"{keyword.replace(' ', '_')}.html"
    file_path = output_folder / file_name
    file_path.write_text("", encoding="utf-8")

print(f"[가격비교] {len(keywords)}개의 빈 HTML이 '{output_folder.as_posix()}'에 생성되었습니다.")

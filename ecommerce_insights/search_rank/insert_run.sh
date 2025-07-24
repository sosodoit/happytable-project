#!/bin/bash

if [ $# -ne 3 ]; then
  echo "사용법: ./insert_run.sh [channel] [start_date: YYYYMMDD] [end_date: YYYYMMDD]"
  echo "예: ./insert_run.sh price_compare 20250518 20250622"
  exit 1
fi

channel="$1"
start="$2"
end="$3"
d="$start"

while [ "$d" -le "$end" ]; do
  echo "실행 날짜: $d / 채널: $channel"
  python insert_search_rank.py --channel "$channel" --date "$d"
  d=$(date -d "$d +1 day" +"%Y%m%d")
done
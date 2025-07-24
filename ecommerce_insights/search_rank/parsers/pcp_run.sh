#!/bin/bash

start="20250518"
end="20250622"
d="$start"

while [ "$d" -le "$end" ]; do
  echo "Running for date: $d"
  python price_compare_parser.py --date "$d"
  d=$(date -d "$d +1 day" +"%Y%m%d")
done
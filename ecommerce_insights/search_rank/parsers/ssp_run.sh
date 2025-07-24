#!/bin/bash

start="20250603"
end="20250622"
d="$start"

while [ "$d" -le "$end" ]; do
  echo "Running for date: $d"
  python smartstore_parser.py --date "$d"
  d=$(date -d "$d +1 day" +"%Y%m%d")
done
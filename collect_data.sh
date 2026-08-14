#!/bin/bash
# Data collection script for A-share daily review
# Date: 2026-08-13

NODE="C:/Users/dhsq/.workbuddy/binaries/node/versions/22.22.2/node.exe"
WD="C:/Users/dhsq/WorkBuddy/AGU/daily-review/tools/westock-data.js"
WT="C:/Users/dhsq/WorkBuddy/AGU/daily-review/tools/westock-tool.js"
OUT="C:/Users/dhsq/WorkBuddy/AGU/daily-review/data"

echo "=== 1. Core Index Quotes ==="
"$NODE" "$WD" quote sh000001,sz399001,sz399006,sh000688,sh000016,sh000300,sh000852,sh000905,sz399303,bj899050 --raw > "$OUT/quote.json" 2>&1
echo "quote.json: $(wc -c < "$OUT/quote.json") bytes"

echo "=== 2. Market Overview ==="
"$NODE" "$WD" market-overview --type all --raw > "$OUT/market_overview.json" 2>&1
echo "market_overview.json: $(wc -c < "$OUT/market_overview.json") bytes"

echo "=== 3. Change Distribution ==="
"$NODE" "$WD" changedist --raw > "$OUT/changedist.json" 2>&1
echo "changedist.json: $(wc -c < "$OUT/changedist.json") bytes"

echo "=== 4. Sector Ranking ==="
"$NODE" "$WD" sector ranking --raw > "$OUT/sector_ranking.json" 2>&1
echo "sector_ranking.json: $(wc -c < "$OUT/sector_ranking.json") bytes"

echo "=== 5. K-line sh000001 day 30 ==="
"$NODE" "$WD" kline sh000001 --period day --limit 30 --raw > "$OUT/kline_sh_day.json" 2>&1
echo "kline_sh_day.json: $(wc -c < "$OUT/kline_sh_day.json") bytes"

echo "=== 6. K-line sh000001 week 12 ==="
"$NODE" "$WD" kline sh000001 --period week --limit 12 --raw > "$OUT/kline_sh_week.json" 2>&1
echo "kline_sh_week.json: $(wc -c < "$OUT/kline_sh_week.json") bytes"

echo "=== 7. K-line sz399303 day 30 ==="
"$NODE" "$WD" kline sz399303 --period day --limit 30 --raw > "$OUT/kline_gz_day.json" 2>&1
echo "kline_gz_day.json: $(wc -c < "$OUT/kline_gz_day.json") bytes"

echo "=== 8. Technical sh000001 ==="
"$NODE" "$WD" technical sh000001 --group macd,kdj,rsi --raw > "$OUT/tech_sh.json" 2>&1
echo "tech_sh.json: $(wc -c < "$OUT/tech_sh.json") bytes"

echo "=== 9. Technical sz399303 ==="
"$NODE" "$WD" technical sz399303 --group macd,kdj,rsi --raw > "$OUT/tech_gz.json" 2>&1
echo "tech_gz.json: $(wc -c < "$OUT/tech_gz.json") bytes"

echo "=== 10. Hot Board ==="
"$NODE" "$WD" hot board > "$OUT/hot_board.json" 2>&1
echo "hot_board.json: $(wc -c < "$OUT/hot_board.json") bytes"

echo "=== 11. Limit-up Ranking ==="
"$NODE" "$WT" ranking limitup_days --limit 20 --raw > "$OUT/limitup.json" 2>&1
echo "limitup.json: $(wc -c < "$OUT/limitup.json") bytes"

echo "=== 12. News Market ==="
"$NODE" "$WD" news market --market hs --limit 15 > "$OUT/news.json" 2>&1
echo "news.json: $(wc -c < "$OUT/news.json") bytes"

echo "=== ALL DONE ==="

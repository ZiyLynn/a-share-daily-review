#!/usr/bin/env bash
# A股每日复盘 - 数据采集脚本
# 在 GitHub Actions 中运行，调用 westock CLI 采集全量数据

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
TOOLS_DIR="$ROOT_DIR/tools"
DATA_DIR="$ROOT_DIR/data"

mkdir -p "$DATA_DIR"

# Node path (in GitHub Actions, node is on PATH; locally use full path)
NODE_BIN="${NODE_BIN:-node}"

WESTOCK_DATA="$TOOLS_DIR/westock-data.js"
WESTOCK_TOOL="$TOOLS_DIR/westock-tool.js"

echo "=== 开始采集A股数据 ==="

# 1. 核心指数行情
echo "[1/12] 核心指数行情..."
"$NODE_BIN" "$WESTOCK_DATA" quote \
  sh000001,sz399001,sz399006,sh000688,sh000016,sh000300,sh000852,sh000905,sh000922,bj899050,sz399303 \
  --raw > "$DATA_DIR/quotes.json" 2>/dev/null

# 2. 市场总览
echo "[2/12] 市场总览..."
"$NODE_BIN" "$WESTOCK_DATA" market-overview --type all --raw > "$DATA_DIR/overview.json" 2>/dev/null

# 3. 涨跌分布
echo "[3/12] 涨跌分布..."
"$NODE_BIN" "$WESTOCK_DATA" changedist --raw > "$DATA_DIR/changedist.json" 2>/dev/null

# 4. 板块排行
echo "[4/12] 板块排行..."
"$NODE_BIN" "$WESTOCK_DATA" sector ranking --raw > "$DATA_DIR/sectors.json" 2>/dev/null

# 5. 上证日K线(30日)
echo "[5/12] 上证日K线..."
"$NODE_BIN" "$WESTOCK_DATA" kline sh000001 --period day --limit 30 --raw > "$DATA_DIR/sh_daily.json" 2>/dev/null

# 6. 上证周K线(12周)
echo "[6/12] 上证周K线..."
"$NODE_BIN" "$WESTOCK_DATA" kline sh000001 --period week --limit 12 --raw > "$DATA_DIR/sh_weekly.json" 2>/dev/null

# 7. 国证2000日K线(30日)
echo "[7/12] 国证2000日K线..."
"$NODE_BIN" "$WESTOCK_DATA" kline sz399303 --period day --limit 30 --raw > "$DATA_DIR/gz_daily.json" 2>/dev/null

# 8. 上证技术指标
echo "[8/12] 上证技术指标..."
"$NODE_BIN" "$WESTOCK_DATA" technical sh000001 --group macd,kdj,rsi --raw > "$DATA_DIR/sh_tech.json" 2>/dev/null

# 9. 国证2000技术指标
echo "[9/12] 国证2000技术指标..."
"$NODE_BIN" "$WESTOCK_DATA" technical sz399303 --group macd,kdj,rsi --raw > "$DATA_DIR/gz_tech.json" 2>/dev/null

# 10. 热门板块
echo "[10/12] 热门板块..."
"$NODE_BIN" "$WESTOCK_DATA" hot board > "$DATA_DIR/hot_board.json" 2>/dev/null

# 11. 连板梯队
echo "[11/12] 连板梯队..."
"$NODE_BIN" "$WESTOCK_TOOL" ranking limitup_days --limit 20 --raw > "$DATA_DIR/limitup_days.json" 2>/dev/null

# 12. 市场新闻
echo "[12/12] 市场新闻..."
"$NODE_BIN" "$WESTOCK_DATA" news market --market hs --limit 15 > "$DATA_DIR/news.json" 2>/dev/null

echo ""
echo "=== 数据采集完成 ==="
ls -lh "$DATA_DIR"/*.json | awk '{print $5, $9}'

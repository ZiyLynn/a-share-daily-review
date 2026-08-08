#!/usr/bin/env bash
# A股每日复盘 - 数据采集脚本
# 在 GitHub Actions 中运行，调用 westock CLI 采集全量数据

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# 切换到项目根目录，使用相对路径（兼容 sandbox 和 GitHub Actions）
cd "$ROOT_DIR"

TOOLS_DIR="tools"
DATA_DIR="data"

mkdir -p "$DATA_DIR"

# Node path (in GitHub Actions, node is on PATH; locally use full path)
NODE_BIN="${NODE_BIN:-node}"

WESTOCK_DATA="$TOOLS_DIR/westock-data.js"
WESTOCK_TOOL="$TOOLS_DIR/westock-tool.js"

# 安全写入函数：先捕获命令输出到变量，非空才写入目标文件
# 用法: safe_fetch "输出文件路径" 命令...
safe_fetch() {
  local outfile="$1"; shift
  local result
  result="$("$@" 2>/dev/null)"
  if [ -n "$result" ]; then
    printf '%s' "$result" > "$outfile"
    echo "  [OK] $(basename "$outfile") ($(printf '%s' "$result" | wc -c) bytes)"
  else
    if [ -s "$outfile" ]; then
      echo "  [WARN] API 无返回，保留旧数据: $(basename "$outfile")"
    else
      echo "  [FAIL] API 无返回且无旧数据: $(basename "$outfile")"
    fi
  fi
}

echo "=== 开始采集A股数据 ==="

# 1. 核心指数行情
echo "[1/13] 核心指数行情..."
safe_fetch "$DATA_DIR/quotes.json" \
  "$NODE_BIN" "$WESTOCK_DATA" quote \
  sh000001,sz399001,sz399006,sh000688,sh000016,sh000300,sh000852,sh000905,sh000922,bj899050,sz399303 \
  --raw

# 2. 市场总览
echo "[2/13] 市场总览..."
safe_fetch "$DATA_DIR/overview.json" \
  "$NODE_BIN" "$WESTOCK_DATA" market-overview --type all --raw

# 3. 涨跌分布
echo "[3/13] 涨跌分布..."
safe_fetch "$DATA_DIR/changedist.json" \
  "$NODE_BIN" "$WESTOCK_DATA" changedist --raw

# 4. 板块排行
echo "[4/13] 板块排行..."
safe_fetch "$DATA_DIR/sectors.json" \
  "$NODE_BIN" "$WESTOCK_DATA" sector ranking --raw

# 5. 上证日K线(30日)
echo "[5/13] 上证日K线..."
safe_fetch "$DATA_DIR/sh_daily.json" \
  "$NODE_BIN" "$WESTOCK_DATA" kline sh000001 --period day --limit 30 --raw

# 6. 上证周K线(12周)
echo "[6/13] 上证周K线..."
safe_fetch "$DATA_DIR/sh_weekly.json" \
  "$NODE_BIN" "$WESTOCK_DATA" kline sh000001 --period week --limit 12 --raw

# 7. 国证2000日K线(30日)
echo "[7/13] 国证2000日K线..."
safe_fetch "$DATA_DIR/gz_daily.json" \
  "$NODE_BIN" "$WESTOCK_DATA" kline sz399303 --period day --limit 30 --raw

# 8. 上证技术指标
echo "[8/13] 上证技术指标..."
safe_fetch "$DATA_DIR/sh_tech.json" \
  "$NODE_BIN" "$WESTOCK_DATA" technical sh000001 --group macd,kdj,rsi --raw

# 9. 国证2000技术指标
echo "[9/13] 国证2000技术指标..."
safe_fetch "$DATA_DIR/gz_tech.json" \
  "$NODE_BIN" "$WESTOCK_DATA" technical sz399303 --group macd,kdj,rsi --raw

# 10. 热门板块
echo "[10/13] 热门板块..."
safe_fetch "$DATA_DIR/hot_board.json" \
  "$NODE_BIN" "$WESTOCK_DATA" hot board

# 11. 连板梯队
echo "[11/13] 连板梯队..."
safe_fetch "$DATA_DIR/limitup_days.json" \
  "$NODE_BIN" "$WESTOCK_TOOL" ranking limitup_days --limit 20 --raw

# 12. 市场新闻
echo "[12/13] 市场新闻..."
safe_fetch "$DATA_DIR/news.json" \
  "$NODE_BIN" "$WESTOCK_DATA" news market --market hs --limit 15

# 13. 主力净流入TOP10
echo "[13/13] 主力净流入TOP10..."
safe_fetch "$DATA_DIR/main_force.json" \
  "$NODE_BIN" "$WESTOCK_TOOL" ranking cap_main_net --limit 10 --raw

echo ""
echo "=== 数据采集完成 ==="

# 数据完整性校验
echo ""
echo "=== 数据完整性校验 ==="
FAIL=0
for f in quotes overview changedist sectors sh_daily sh_weekly gz_daily sh_tech limitup_days main_force; do
  FILE="$DATA_DIR/${f}.json"
  if [ ! -s "$FILE" ]; then
    echo "  [FAIL] ${f}.json 为空或不存在"
    FAIL=1
  else
    SIZE=$(wc -c < "$FILE")
    echo "  [OK] ${f}.json (${SIZE} bytes)"
  fi
done
if [ "$FAIL" = "1" ]; then
  echo ""
  echo "ERROR: 部分核心数据文件缺失，请检查 API 连通性"
  exit 1
fi
echo ""
echo "所有核心数据文件校验通过"

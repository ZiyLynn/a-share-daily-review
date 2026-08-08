#!/usr/bin/env python3
"""
A股每日技术复盘 - GitHub Actions 自动生成脚本
完全自包含，不依赖 WorkBuddy 本地环境
"""
import json, math, os, sys
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.join(SCRIPT_DIR, "..")
DATA_DIR = os.path.join(ROOT_DIR, "data")

# ========== 数据加载 ==========
class DataLoadError(RuntimeError):
    '''Raised when a required westock data file cannot be loaded safely.'''


def load_json(name):
    p = os.path.join(DATA_DIR, name + ".json")
    try:
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError as exc:
        raise DataLoadError(f'Missing required westock data file: {p}') from exc
    except json.JSONDecodeError as exc:
        raise DataLoadError(
            f'Invalid JSON in {p} at line {exc.lineno}, column {exc.colno}: {exc.msg}'
        ) from exc
    except OSError as exc:
        raise DataLoadError(f'Cannot read westock data file {p}: {exc}') from exc

def unwrap(d):
    if isinstance(d, dict) and d.get("success") and "data" in d:
        return d["data"]
    return d

def load_all():
    raw = {
        "quotes": load_json("quotes"),
        "overview": load_json("overview"),
        "changedist": load_json("changedist"),
        "sectors": load_json("sectors"),
        "sh_daily": load_json("sh_daily"),
        "sh_weekly": load_json("sh_weekly"),
        "gz_daily": load_json("gz_daily"),
        "sh_tech": load_json("sh_tech"),
        "gz_tech": load_json("gz_tech"),
        "limitup_days": load_json("limitup_days"),
        "main_force": load_json("main_force"),
    }
    raw["quotes"] = unwrap(raw["quotes"])
    raw["sh_tech"] = unwrap(raw["sh_tech"])
    raw["gz_tech"] = unwrap(raw["gz_tech"])
    return raw

def get_quote(quotes, code):
    if not quotes: return {}
    for q in quotes:
        d = q.get("data", q) if isinstance(q, dict) else {}
        if d.get("code") == code or d.get("symbol") == code:
            return d
    return {}

def fmt_code(code):
    """把 westock 原始代码(sh603773/sz001267/bj899050)格式化为标准展示: 603773.SH / 001267.SZ / 899050.BJ"""
    if not code: return ""
    code = str(code).strip().lower()
    if code.startswith("sh"):
        return code[2:] + ".SH"
    if code.startswith("sz"):
        return code[2:] + ".SZ"
    if code.startswith("bj"):
        return code[2:] + ".BJ"
    return code.upper()

def get_overview_row(overview, idx):
    if not overview or idx >= len(overview):
        return {}
    item = overview[idx]
    return item.get("row", {}) or {}

def require_fields(mapping, fields, context):
    if not isinstance(mapping, dict):
        raise DataLoadError(f'{context} must be an object')
    missing = [key for key in fields if mapping.get(key) is None]
    if missing:
        raise DataLoadError(f'{context} is missing required fields: {", ".join(missing)}')

def require_numbers(mapping, fields, context):
    require_fields(mapping, fields, context)
    invalid = []
    for key in fields:
        try:
            value = float(mapping[key])
            if isinstance(mapping[key], bool) or not math.isfinite(value):
                invalid.append(key)
        except (TypeError, ValueError):
            invalid.append(key)
    if invalid:
        raise DataLoadError(f'{context} has invalid numeric fields: {", ".join(invalid)}')

def validate_westock_data(data):
    """Reject incomplete westock responses instead of fabricating zero-value output."""
    list_sources = ('quotes', 'overview', 'sh_daily', 'sh_weekly', 'gz_daily',
                    'limitup_days', 'main_force')
    dict_sources = ('changedist', 'sectors', 'sh_tech', 'gz_tech')
    for name in list_sources:
        if not isinstance(data.get(name), list):
            raise DataLoadError(f'{name}.json did not return the expected list')
    for name in dict_sources:
        if not isinstance(data.get(name), dict):
            raise DataLoadError(f'{name}.json did not return the expected object')

    required_quotes = ('sh000001', 'sz399001', 'sz399006', 'sh000852', 'sz399303')
    for code in required_quotes:
        quote = get_quote(data['quotes'], code)
        require_fields(quote, ('price', 'change_percent', 'chg_5d', 'time'), f'quotes[{code}]')
        require_numbers(quote, ('price', 'change_percent', 'chg_5d'), f'quotes[{code}]')
    require_fields(get_quote(data['quotes'], 'sh000001'), ('chg_60d',), 'quotes[sh000001]')
    require_fields(get_quote(data['quotes'], 'sz399303'), ('volume_ratio',), 'quotes[sz399303]')
    require_numbers(get_quote(data['quotes'], 'sh000001'), ('chg_60d',), 'quotes[sh000001]')
    require_numbers(get_quote(data['quotes'], 'sz399303'), ('volume_ratio',), 'quotes[sz399303]')

    if len(data['overview']) < 5:
        raise DataLoadError('overview.json is missing required market overview rows')
    require_fields(get_overview_row(data['overview'], 0),
                   ('STOCK_WIDTH_SCORE', 'STOCK_WIDTH_STATUS', 'SECTOR_WIDTH_SCORE',
                    'SECTOR_WIDTH_STATUS', 'SENTIMENT_SCORE', 'SENTIMENT_STATUS',
                    'TECHNICAL_SCORE', 'TECHNICAL_STATUS', 'STYLE_ROTATION_SCORE',
                    'STYLE_ROTATION_STATUS', 'SECTOR_ROTATION_SCORE', 'SECTOR_ROTATION_STATUS'),
                   'overview summary row')
    require_numbers(get_overview_row(data['overview'], 0),
                    ('STOCK_WIDTH_SCORE', 'SECTOR_WIDTH_SCORE', 'SENTIMENT_SCORE',
                     'TECHNICAL_SCORE', 'STYLE_ROTATION_SCORE', 'SECTOR_ROTATION_SCORE'),
                    'overview summary row')
    require_fields(get_overview_row(data['overview'], 1),
                   ('MONEY', 'MONEY_5DAVG', 'MONEY_60DAVG', 'MONEY_5DAVG_RATIO', 'MONEY_60DAVG_RATIO'),
                   'overview trade row')
    require_numbers(get_overview_row(data['overview'], 1),
                    ('MONEY', 'MONEY_5DAVG', 'MONEY_60DAVG', 'MONEY_5DAVG_RATIO', 'MONEY_60DAVG_RATIO'),
                    'overview trade row')
    require_fields(get_overview_row(data['overview'], 3),
                   ('MA_5', 'MA_10', 'MA_20', 'MA_60', 'BOLL_UPPER', 'BOLL_MID', 'BOLL_LOWER'),
                   'overview technical row')
    require_numbers(get_overview_row(data['overview'], 3),
                    ('MA_5', 'MA_10', 'MA_20', 'MA_60', 'BOLL_UPPER', 'BOLL_MID', 'BOLL_LOWER'),
                    'overview technical row')
    require_fields(data['changedist'],
                   ('upCount', 'downCount', 'upLimitCount', 'downLimitCount', 'detail'),
                   'changedist')
    require_numbers(data['changedist'], ('upCount', 'downCount', 'upLimitCount', 'downLimitCount'),
                    'changedist')
    updown = get_overview_row(data['overview'], 4)
    breadth_fields = tuple(f'CNT_{side}{period}' for side in ('HIGH', 'LOW')
                           for period in (5, 20, 60, 120, 250))
    require_fields(updown, breadth_fields, 'overview breadth row')
    require_numbers(updown, breadth_fields, 'overview breadth row')
    sections = data['sectors'].get('sections')
    if not isinstance(sections, list) or len(sections) < 2:
        raise DataLoadError('sectors.json is missing industry or concept rankings')
    for section_index, section in enumerate(sections[:2]):
        if not isinstance(section, list):
            raise DataLoadError(f'sectors.sections[{section_index}] must be a list')
        if not section:
            raise DataLoadError(f'sectors.sections[{section_index}] must not be empty')
        for item_index, item in enumerate(section):
            require_fields(item, ('name', 'changePct', 'changePct5d', 'leadStock'),
                           f'sectors.sections[{section_index}][{item_index}]')
            require_numbers(item, ('changePct', 'changePct5d'),
                            f'sectors.sections[{section_index}][{item_index}]')
    if any(len(data[name]) < 2 for name in ('sh_daily', 'sh_weekly', 'gz_daily')):
        raise DataLoadError('westock K-line responses must contain at least two records')
    for name in ('sh_daily', 'sh_weekly', 'gz_daily'):
        for index, item in enumerate(data[name]):
            require_fields(item, ('date', 'open', 'high', 'low', 'last', 'amount'), f'{name}[{index}]')
            require_numbers(item, ('open', 'high', 'low', 'last', 'amount'), f'{name}[{index}]')
    for index, item in enumerate(data['changedist']['detail']):
        require_fields(item, ('section', 'count', 'flag'), f'changedist.detail[{index}]')
        require_numbers(item, ('count', 'flag'), f'changedist.detail[{index}]')

    for source, code in (('sh_tech', 'sh000001'), ('gz_tech', 'sz399303')):
        tech = data[source].get(code)
        require_fields(tech, ('macd', 'kdj', 'rsi'), f'{source}[{code}]')
        require_fields(tech['macd'], ('DIF', 'DEA', 'MACD'), f'{source}[{code}].macd')
        require_fields(tech['kdj'], ('KDJ_K', 'KDJ_D', 'KDJ_J'), f'{source}[{code}].kdj')
        require_numbers(tech['macd'], ('DIF', 'DEA', 'MACD'), f'{source}[{code}].macd')
        require_numbers(tech['kdj'], ('KDJ_K', 'KDJ_D', 'KDJ_J'), f'{source}[{code}].kdj')
    require_fields(data['sh_tech']['sh000001']['rsi'], ('RSI_6',), 'sh_tech[sh000001].rsi')
    require_numbers(data['sh_tech']['sh000001']['rsi'], ('RSI_6',), 'sh_tech[sh000001].rsi')

    for index, item in enumerate(data['limitup_days']):
        require_fields(item, ('LimitUpDays', '名称', '代码'), f'limitup_days[{index}]')
        require_numbers(item, ('LimitUpDays',), f'limitup_days[{index}]')
    for index, item in enumerate(data['main_force']):
        require_fields(item, ('MainNetIn', '名称', '代码'), f'main_force[{index}]')
        require_numbers(item, ('MainNetIn',), f'main_force[{index}]')

# ========== 格式化 ==========
def f2(n):
    if n is None: return "--"
    try: return f"{float(n):.2f}"
    except: return str(n)

def fp(n):
    if n is None: return "--"
    try: return f"{float(n):+.2f}%"
    except: return str(n)

def fa(n):
    if n is None: return "--"
    try:
        v = float(n)
        if v > 10000: return f"{v:.0f}亿"
        return f"{v:.0f}亿"
    except: return str(n)

# ========== 分析 ==========
def analyze(data):
    quotes = data.get("quotes", [])
    overview = data.get("overview", [])
    cd = data.get("changedist", {})
    sectors = data.get("sectors", {})
    sh_daily = data.get("sh_daily", [])
    sh_weekly = data.get("sh_weekly", [])
    gz_daily = data.get("gz_daily", [])
    sh_tech = data.get("sh_tech", {})
    gz_tech = data.get("gz_tech", {})
    limitup = data.get("limitup_days", [])
    main_force = data.get("main_force", [])

    sh = get_quote(quotes, "sh000001")
    gz = get_quote(quotes, "sz399303")
    sz = get_quote(quotes, "sz399001")
    cyb = get_quote(quotes, "sz399006")
    zz1000 = get_quote(quotes, "sh000852")

    summary = get_overview_row(overview, 0)
    trade = get_overview_row(overview, 1)
    interval = get_overview_row(overview, 2)
    technical = get_overview_row(overview, 3)
    updown = get_overview_row(overview, 4)
    rotation = get_overview_row(overview, 7)

    sh_t = sh_tech.get("sh000001", {}) if isinstance(sh_tech, dict) else {}
    gz_t = gz_tech.get("sz399303", {}) if isinstance(gz_tech, dict) else {}
    macd = sh_t.get("macd", {})
    kdj = sh_t.get("kdj", {})
    rsi = sh_t.get("rsi", {})
    gz_macd = gz_t.get("macd", {})
    gz_kdj = gz_t.get("kdj", {})

    ma5 = technical["MA_5"]
    ma10 = technical["MA_10"]
    ma20 = technical["MA_20"]
    ma60 = technical["MA_60"]
    boll_upper = technical["BOLL_UPPER"]
    boll_mid = technical["BOLL_MID"]
    boll_lower = technical["BOLL_LOWER"]

    dif = macd["DIF"]
    dea = macd["DEA"]
    macd_val = macd["MACD"]
    j_val = kdj["KDJ_J"]
    k_val = kdj["KDJ_K"]
    d_val = kdj["KDJ_D"]
    rsi6 = rsi["RSI_6"]

    gz_dif = gz_macd["DIF"]
    gz_dea = gz_macd["DEA"]
    gz_macd_val = gz_macd["MACD"]
    gz_j = gz_kdj["KDJ_J"]

    sh_price = sh["price"]
    sh_chg = sh["change_percent"]
    gz_price = gz["price"]
    gz_chg = gz["change_percent"]

    is_golden = dif > dea
    is_above_ma5 = sh_price > ma5 if ma5 else True
    is_above_ma20 = sh_price > ma20 if ma20 else True
    is_above_ma60 = sh_price > ma60 if ma60 else False
    is_overbought = j_val > 100
    macd_above_zero = dif > 0

    bull = sum([is_golden, is_above_ma5, is_above_ma20, sh_chg > 0, gz_chg > 0, macd_val > 0])
    signal_label = "偏强" if bull >= 5 else "中性偏强" if bull >= 3 else "中性偏弱" if bull >= 2 else "偏弱"

    sec = sectors.get("sections", []) if isinstance(sectors, dict) else []
    industry_top = sec[0] if len(sec) > 0 else []
    concept_top = sec[1] if len(sec) > 1 else []
    all_ind = sorted(industry_top, key=lambda x: float(x["changePct"]), reverse=True) if industry_top else []
    top_sectors = all_ind[:5]

    max_streak = max([int(x["LimitUpDays"]) for x in (limitup or [])], default=0)
    top_streaks = (limitup or [])[:5]

    money_yi = trade["MONEY"]
    money_60d_ratio = trade["MONEY_60DAVG_RATIO"]

    # 涨跌家数和涨跌停家数统一使用 changedist，禁止跨接口混算比例。
    up_count = cd["upCount"]
    down_count = cd["downCount"]
    up_limit = cd["upLimitCount"]
    down_limit = cd["downLimitCount"]
    high60 = updown["CNT_HIGH60"]
    low60 = updown["CNT_LOW60"]

    # 市场宽度细节
    width_scores = {
        "stock_width": (summary["STOCK_WIDTH_SCORE"], summary["STOCK_WIDTH_STATUS"]),
        "sector_width": (summary["SECTOR_WIDTH_SCORE"], summary["SECTOR_WIDTH_STATUS"]),
        "sentiment": (summary["SENTIMENT_SCORE"], summary["SENTIMENT_STATUS"]),
        "tech": (summary["TECHNICAL_SCORE"], summary["TECHNICAL_STATUS"]),
        "style_rot": (summary["STYLE_ROTATION_SCORE"], summary["STYLE_ROTATION_STATUS"]),
        "sector_rot": (summary["SECTOR_ROTATION_SCORE"], summary["SECTOR_ROTATION_STATUS"]),
    }
    new_highs = {p: updown[f"CNT_HIGH{p}"] for p in [5, 20, 60, 120, 250]}
    new_lows = {p: updown[f"CNT_LOW{p}"] for p in [5, 20, 60, 120, 250]}

    # 主力资金TOP10
    main_force_top = []
    for s in (main_force or [])[:10]:
        net = s["MainNetIn"]
        main_force_top.append({
            "name": s["名称"],
            "code": s["代码"],
            "net": net / 1e4,  # 万→亿
        })

    # K线数据为倒序（[0]=最新），趋势判断用最新两条
    daily_trend = "多头" if sh_daily[0]["last"] > sh_daily[1]["last"] else "偏空"
    weekly_trend = "多头" if sh_weekly[0]["last"] > sh_weekly[1]["last"] else "偏空"
    monthly_trend = "多头" if sh["chg_60d"] > 0 else "空头"
    vol_healthy = (sh_chg > 0 and money_60d_ratio > 100) or (sh_chg < 0 and money_60d_ratio < 100)

    return dict(
        date=sh["time"],
        sh=sh, gz=gz, sz=sz, cyb=cyb, zz1000=zz1000,
        summary=summary, trade=trade, technical=technical, updown=updown, rotation=rotation,
        cd=cd, sh_daily=sh_daily, sh_weekly=sh_weekly, gz_daily=gz_daily,
        dif=dif, dea=dea, macd_val=macd_val, j_val=j_val, k_val=k_val, d_val=d_val, rsi6=rsi6,
        gz_dif=gz_dif, gz_dea=gz_dea, gz_macd_val=gz_macd_val, gz_j=gz_j,
        ma5=ma5, ma10=ma10, ma20=ma20, ma60=ma60,
        boll_upper=boll_upper, boll_mid=boll_mid, boll_lower=boll_lower,
        is_golden=is_golden, is_overbought=is_overbought,
        is_above_ma5=is_above_ma5, is_above_ma20=is_above_ma20, is_above_ma60=is_above_ma60,
        macd_above_zero=macd_above_zero,
        bull_score=bull, signal_label=signal_label,
        top_sectors=top_sectors, concept_top=concept_top[:6],
        max_streak=max_streak, top_streaks=top_streaks,
        money_yi=money_yi, money_5d_avg=trade["MONEY_5DAVG"],
        money_60d_avg=trade["MONEY_60DAVG"], money_60d_ratio=money_60d_ratio,
        up_count=up_count, down_count=down_count, up_limit=up_limit, down_limit=down_limit,
        high60=high60, low60=low60,
        width_scores=width_scores, new_highs=new_highs, new_lows=new_lows,
        main_force_top=main_force_top,
        daily_trend=daily_trend, weekly_trend=weekly_trend, monthly_trend=monthly_trend,
        vol_healthy=vol_healthy,
    )

# ========== SVG 生成 ==========
def kline_svg(klines, title):
    if not klines: return "<p>无K线数据</p>"
    n = len(klines); w=600; h=280; pl=40; pr=10; pt=20; pb=30
    pw=w-pl-pr; ph=h-pt-pb
    highs=[float(k.get("high",0)) for k in klines]
    lows=[float(k.get("low",0)) for k in klines]
    ymx=max(highs)*1.01; ymn=min(lows)*0.99; yr=ymx-ymn or 1
    bw=pw/n*0.7; gp=pw/n*0.3
    def y(v): return pt+ph*(ymx-v)/yr
    def x(i): return pl+i*(bw+gp)+gp/2
    svg=""
    for i,k in enumerate(klines):
        o=float(k.get("open",0)); c=float(k.get("last",k.get("close",0)))
        hi=float(k.get("high",0)); lo=float(k.get("low",0))
        cx=x(i)+bw/2; up=c>=o; col="#ef4444" if up else "#22c55e"
        bt=y(max(o,c)); bh=max(abs(y(o)-y(c)),1)
        svg+=f'<line x1="{cx:.1f}" y1="{y(hi):.1f}" x2="{cx:.1f}" y2="{y(lo):.1f}" stroke="{col}" stroke-width="1"/>'
        svg+=f'<rect x="{x(i):.1f}" y="{bt:.1f}" width="{bw:.1f}" height="{bh:.1f}" fill="{col}"/>'
    yl=""
    for i in range(5):
        v=ymx-yr*i/4; yp=pt+ph*i/4
        yl+=f'<text x="{pl-5}" y="{yp+4}" text-anchor="end" font-size="10" fill="#8b949e">{v:.0f}</text>'
    xl=""
    for i in range(0,n,max(1,n//5)):
        ds=klines[i].get("date","")[5:]; xp=x(i)+bw/2
        xl+=f'<text x="{xp:.1f}" y="{h-10}" text-anchor="middle" font-size="9" fill="#8b949e">{ds}</text>'
    return f'<svg viewBox="0 0 {w} {h}" style="width:100%;height:auto" xmlns="http://www.w3.org/2000/svg"><rect width="{w}" height="{h}" fill="#0d1117"/><text x="{w/2}" y="14" text-anchor="middle" font-size="13" font-weight="bold" fill="#c9d1d9">{title}</text><line x1="{pl}" y1="{pt}" x2="{pl}" y2="{pt+ph}" stroke="#30363d"/><line x1="{pl}" y1="{pt+ph}" x2="{w-pr}" y2="{pt+ph}" stroke="#30363d"/>{yl}{xl}{svg}</svg>'

def dist_svg(cd):
    items = [d for d in (cd.get("detail",[]) if cd else []) if d.get("section") not in ("平",)]
    if not items: return "<p>无数据</p>"
    w=600;h=280;pl=40;pr=10;pt=24;pb=36;pw=w-pl-pr;ph=h-pt-pb
    n=len(items); mx=max(d.get("count",0) for d in items) or 1
    bw=pw/n*0.8; svg=""
    for i,d in enumerate(items):
        cnt=d.get("count",0); flag=d.get("flag",0)
        col="#ef4444" if flag>=0 else "#22c55e"
        bh=ph*cnt/mx; bx=pl+i*(pw/n)+(pw/n-bw)/2; by=pt+ph-bh
        svg+=f'<rect x="{bx:.1f}" y="{by:.1f}" width="{bw:.1f}" height="{bh:.1f}" fill="{col}" rx="2"/>'
        svg+=f'<text x="{bx+bw/2:.1f}" y="{h-12}" text-anchor="middle" font-size="8" fill="#8b949e">{d.get("section","")}</text>'
        svg+=f'<text x="{bx+bw/2:.1f}" y="{by-3:.1f}" text-anchor="middle" font-size="8" fill="{col}">{cnt}</text>'
    return f'<svg viewBox="0 0 {w} {h}" style="width:100%;height:auto" xmlns="http://www.w3.org/2000/svg"><rect width="{w}" height="{h}" fill="#0d1117"/><text x="{w/2}" y="14" text-anchor="middle" font-size="12" fill="#c9d1d9">涨跌分布</text>{svg}</svg>'

def sector_svg(top_sectors):
    if not top_sectors: return "<p>无数据</p>"
    w=600;h=280;pl=80;pr=40;pt=24;pb=16;pw=w-pl-pr;ph=h-pt-pb
    n=len(top_sectors); mx=max(abs(float(s.get("changePct",0))) for s in top_sectors) or 1
    svg=""
    for i,s in enumerate(top_sectors):
        pct=float(s.get("changePct",0)); bw=pw*abs(pct)/mx
        by=pt+i*(ph/n)+4; bh=ph/n-8; col="#ef4444" if pct>=0 else "#22c55e"
        nm=s.get("name","")[:8]
        svg+=f'<text x="{pl-5}" y="{by+bh/2+4}" text-anchor="end" font-size="10" fill="#c9d1d9">{nm}</text>'
        svg+=f'<rect x="{pl}" y="{by:.1f}" width="{bw:.1f}" height="{bh:.1f}" fill="{col}" rx="2"/>'
        svg+=f'<text x="{pl+bw+5:.1f}" y="{by+bh/2+4}" font-size="10" fill="{col}">{pct:+.2f}%</text>'
    return f'<svg viewBox="0 0 {w} {h}" style="width:100%;height:auto" xmlns="http://www.w3.org/2000/svg"><rect width="{w}" height="{h}" fill="#0d1117"/><text x="{w/2}" y="14" text-anchor="middle" font-size="12" fill="#c9d1d9">领涨行业板块</text>{svg}</svg>'

def rs_svg(sh, sz, cyb, zz1000, gz):
    # 5日相对强弱：以"上证"为基准(=0%)，其他指数 = 自身5日涨幅 - 上证5日涨幅
    w=600;h=280;pl=90;pr=28;pt=34;pb=28;pw=w-pl-pr
    base = sh.get("chg_5d", 0)
    raw = [("上证",sh.get("chg_5d",0)),
           ("深成指",sz.get("chg_5d",0)),
           ("创业板",cyb.get("chg_5d",0)),
           ("中证1000",zz1000.get("chg_5d",0)),
           ("国证2000",gz.get("chg_5d",0))]
    items = [(nm, chg - base) for (nm, chg) in raw]   # 转成相对差值
    # 决定横轴量级：取绝对值最大者，再至少 1% 留白；上界 4% 起步
    mx = max(abs(v) for _, v in items) or 1
    rng = max(mx * 1.2, 1.0, 4.0)   # 量程，5 段刻度
    rng = max(round(rng + 0.5), 1)   # 取整
    # 零轴 x 坐标
    cx = pl + pw * 0.5
    n = len(items); ph_h = h - pt - pb
    bw = ph_h / n * 0.62
    svg = ""
    # 边框
    svg += f'<line x1="{pl}" y1="{pt}" x2="{pl}" y2="{pt+ph_h}" stroke="#30363d"/>'
    svg += f'<line x1="{pl}" y1="{pt+ph_h}" x2="{w-pr}" y2="{pt+ph_h}" stroke="#30363d"/>'
    # 零轴（基准线）
    svg += f'<line x1="{cx}" y1="{pt}" x2="{cx}" y2="{pt+ph_h}" stroke="#6e7681" stroke-width="1" stroke-dasharray="2,2"/>'
    # X 轴刻度
    for tick in [-rng, -rng/2, 0, rng/2, rng]:
        tx = cx + pw * 0.5 * (tick / rng)
        svg += f'<line x1="{tx}" y1="{pt+ph_h}" x2="{tx}" y2="{pt+ph_h+3}" stroke="#30363d"/>'
        label = "基准" if tick == 0 else f"{tick:+.1f}%"
        svg += f'<text x="{tx}" y="{pt+ph_h+13}" text-anchor="middle" font-size="9" fill="#8b949e">{label}</text>'
    # 柱体
    for i, (nm, rel) in enumerate(items):
        by = pt + i * (ph_h / n) + (ph_h / n - bw) / 2
        # 基准（上证）画灰色
        if i == 0:
            col = "#6e7681"
            blen = 6
            svg += f'<rect x="{cx-blen/2:.1f}" y="{by:.1f}" width="{blen}" height="{bw:.1f}" fill="{col}" rx="2"/>'
            svg += f'<text x="{cx+blen/2+4:.1f}" y="{by+bw/2+4}" font-size="9" fill="{col}">{rel:+.1f}% (基准)</text>'
        else:
            col = "#ef4444" if rel >= 0 else "#22c55e"
            blen = (pw * 0.5) * abs(rel) / rng
            if rel >= 0:
                svg += f'<rect x="{cx:.1f}" y="{by:.1f}" width="{blen:.1f}" height="{bw:.1f}" fill="{col}" rx="2"/>'
                svg += f'<text x="{cx+blen+4:.1f}" y="{by+bw/2+4}" font-size="9" fill="{col}">{rel:+.1f}%</text>'
            else:
                svg += f'<rect x="{cx-blen:.1f}" y="{by:.1f}" width="{blen:.1f}" height="{bw:.1f}" fill="{col}" rx="2"/>'
                svg += f'<text x="{cx-blen-4:.1f}" y="{by+bw/2+4}" text-anchor="end" font-size="9" fill="{col}">{rel:+.1f}%</text>'
        # 左侧名称
        svg += f'<text x="{pl-6}" y="{by+bw/2+4}" text-anchor="end" font-size="10" fill="#c9d1d9">{nm}</text>'
    # 顶部标题（只此一个，不重叠）
    return f'<svg viewBox="0 0 {w} {h}" style="width:100%;height:auto" xmlns="http://www.w3.org/2000/svg"><rect width="{w}" height="{h}" fill="#0d1117"/><text x="{w/2}" y="16" text-anchor="middle" font-size="12" font-weight="bold" fill="#c9d1d9">5日相对强弱（vs 上证）</text>{svg}</svg>'

def vol_svg(sh_daily):
    kl = (sh_daily or [])[:10][::-1]  # 取最新10条并反转为时间正序（旧→新）
    if not kl: return "<p>无数据</p>"
    w=600;h=280;pl=40;pr=10;pt=20;pb=30;pw=w-pl-pr;ph=h-pt-pb
    n=len(kl); mx=max(float(k.get("amount",0)) for k in kl) or 1; svg=""
    for i,k in enumerate(kl):
        vol=float(k.get("amount",0)); o=float(k.get("open",0)); c=float(k.get("last",0))
        col="#ef4444" if c>=o else "#22c55e"; bw=pw/n*0.7
        bx=pl+i*(pw/n)+(pw/n-bw)/2; bh=ph*vol/mx; by=pt+ph-bh
        svg+=f'<rect x="{bx:.1f}" y="{by:.1f}" width="{bw:.1f}" height="{bh:.1f}" fill="{col}" opacity="0.8" rx="1"/>'
        svg+=f'<text x="{bx+bw/2:.1f}" y="{h-10}" text-anchor="middle" font-size="7" fill="#8b949e">{k.get("date","")[5:]}</text>'
    return f'<svg viewBox="0 0 {w} {h}" style="width:100%;height:auto" xmlns="http://www.w3.org/2000/svg"><rect width="{w}" height="{h}" fill="#0d1117"/><text x="{w/2}" y="14" text-anchor="middle" font-size="12" fill="#c9d1d9">近10日成交额</text>{svg}</svg>'

def width_svg(new_highs, new_lows):
    """市场宽度：新高新低对比柱状图"""
    w=600;h=280;pl=45;pr=10;pt=24;pb=30;pw=w-pl-pr;ph=h-pt-pb
    periods=[5,20,60,120,250]
    labels=["5日","20日","月(20)","季(60)","半年(120)","年(250)"]
    # 实际用5个周期
    pairs=[(5,"5日"),(20,"20日"),(60,"60日"),(120,"120日"),(250,"250日")]
    n=len(pairs); gap=pw/n; bw=gap*0.32
    mx=max(max(new_highs.values()),max(new_lows.values()),1)
    svg=f'<rect width="{w}" height="{h}" fill="#0d1117"/>'
    svg+=f'<text x="{w/2}" y="16" text-anchor="middle" font-size="12" font-weight="bold" fill="#c9d1d9">新高 vs 新低 对比</text>'
    # Y轴刻度
    for tick in [0, mx//2 if mx>4 else mx//2, mx]:
        ty=pt+ph-ph*tick/mx
        svg+=f'<line x1="{pl}" y1="{ty:.1f}" x2="{w-pr}" y2="{ty:.1f}" stroke="#21262d" stroke-width="0.5"/>'
        svg+=f'<text x="{pl-4}" y="{ty+3:.1f}" text-anchor="end" font-size="8" fill="#6e7681">{int(tick)}</text>'
    for i,(p,label) in enumerate(pairs):
        cx=pl+i*gap+gap/2
        hi=new_highs.get(p,0); lo=new_lows.get(p,0)
        # 新高柱（红，左）
        bh1=ph*hi/mx; by1=pt+ph-bh1
        svg+=f'<rect x="{cx-bw-1:.1f}" y="{by1:.1f}" width="{bw:.1f}" height="{bh1:.1f}" fill="#ef4444" rx="1"/>'
        svg+=f'<text x="{cx-bw/2-1:.1f}" y="{by1-3:.1f}" text-anchor="middle" font-size="7" fill="#ef4444">{hi}</text>'
        # 新低柱（绿，右）
        bh2=ph*lo/mx; by2=pt+ph-bh2
        svg+=f'<rect x="{cx+1:.1f}" y="{by2:.1f}" width="{bw:.1f}" height="{bh2:.1f}" fill="#22c55e" rx="1"/>'
        svg+=f'<text x="{cx+bw/2+1:.1f}" y="{by2-3:.1f}" text-anchor="middle" font-size="7" fill="#22c55e">{lo}</text>'
        # X轴标签
        svg+=f'<text x="{cx:.1f}" y="{h-12}" text-anchor="middle" font-size="8" fill="#8b949e">{label}</text>'
    svg+=f'<text x="{pl-4}" y="{h-2}" text-anchor="end" font-size="7" fill="#ef4444">■新高</text>'
    svg+=f'<text x="{w-pr}" y="{h-2}" text-anchor="end" font-size="7" fill="#22c55e">■新低</text>'
    return f'<svg viewBox="0 0 {w} {h}" style="width:100%;height:auto" xmlns="http://www.w3.org/2000/svg">{svg}</svg>'

def force_svg(main_force_top):
    """主力资金TOP10横向条形图"""
    if not main_force_top: return "<p>无数据</p>"
    w=600;h=280;pl=80;pr=60;pt=22;pb=12;pw=w-pl-pr;ph=h-pt-pb
    n=len(main_force_top); bh=ph/n*0.65; gap=ph/n*0.35
    mx=max(abs(s["net"]) for s in main_force_top) or 1
    svg=f'<rect width="{w}" height="{h}" fill="#0d1117"/>'
    svg+=f'<text x="{w/2}" y="15" text-anchor="middle" font-size="12" font-weight="bold" fill="#c9d1d9">主力净流入TOP10（亿元）</text>'
    # 零轴
    cx=pl+pw*0.5
    svg+=f'<line x1="{cx}" y1="{pt}" x2="{cx}" y2="{pt+ph}" stroke="#30363d" stroke-width="0.5" stroke-dasharray="2,2"/>'
    for i,s in enumerate(main_force_top):
        by=pt+i*(bh+gap)+gap/2
        net=s["net"]; col="#ef4444" if net>=0 else "#22c55e"
        blen=pw*0.5*abs(net)/mx
        name=s["name"][:4]
        if net>=0:
            svg+=f'<rect x="{cx:.1f}" y="{by:.1f}" width="{blen:.1f}" height="{bh:.1f}" fill="{col}" rx="2"/>'
            svg+=f'<text x="{cx+blen+4:.1f}" y="{by+bh/2+3:.1f}" font-size="9" fill="{col}">{net:+.2f}亿</text>'
        else:
            svg+=f'<rect x="{cx-blen:.1f}" y="{by:.1f}" width="{blen:.1f}" height="{bh:.1f}" fill="{col}" rx="2"/>'
            svg+=f'<text x="{cx-blen-4:.1f}" y="{by+bh/2+3:.1f}" text-anchor="end" font-size="9" fill="{col}">{net:+.2f}亿</text>'
        svg+=f'<text x="{pl-6}" y="{by+bh/2+3:.1f}" text-anchor="end" font-size="9" fill="#c9d1d9">{name}</text>'
    return f'<svg viewBox="0 0 {w} {h}" style="width:100%;height:auto" xmlns="http://www.w3.org/2000/svg">{svg}</svg>'

# ========== CSS / JS ==========
CSS = """
*{margin:0;padding:0;box-sizing:border-box}
body{background:#0d1117;color:#c9d1d9;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;line-height:1.6;max-width:1480px;margin:0 auto;padding:16px}
@media(max-width:1100px){body{max-width:100%;padding:10px}}
h1{font-size:1.4rem;text-align:center;margin:8px 0;color:#f0f6fc}
h2{font-size:1.05rem;color:#58a6ff;margin:0 0 8px;padding-bottom:4px;border-bottom:1px solid #21262d}
h3{font-size:0.9rem;color:#8b949e;margin:8px 0 4px}
.card{background:#161b22;border:1px solid #30363d;border-radius:8px;padding:14px;margin-bottom:12px;display:flex;flex-direction:column}
.layout{display:grid;grid-template-columns:1fr 1fr;gap:12px}
@media(max-width:1100px){.layout{grid-template-columns:1fr}}
.layout>.card{margin-bottom:0}
.card[data-span="2"]{grid-column:1/-1}
.beginner-signal{display:flex;gap:6px;flex-wrap:wrap;margin:8px 0}
.beginner-signal>div{background:#21262d;border:1px solid #30363d;border-radius:6px;padding:4px 10px;font-size:0.8rem;text-align:center;flex:1;min-width:100px}
.beginner-signal>div>span{display:block;font-size:0.7rem;color:#8b949e;margin-bottom:2px}
.beginner-signal>div>b{font-size:0.85rem;color:#f0f6fc}
.beginner-box{background:#0c2240;border-left:3px solid #58a6ff;border-radius:4px;padding:8px 12px;margin:8px 0 0;font-size:0.82rem}
.beginner-box .action{color:#7ee787;margin-top:4px;font-weight:600;display:block}
.card-body{flex:1;display:flex;flex-direction:column;min-height:0}
.card:has(.beginner-box) .card-body>.chart-box{margin-top:auto}
.card-body>.chart-box:first-child{margin-top:0}
.tip-dot{display:inline-block;width:16px;height:16px;border-radius:50%;background:#30363d;color:#8b949e;text-align:center;line-height:16px;font-size:10px;cursor:pointer;vertical-align:middle;margin-left:2px;position:relative;user-select:none;-webkit-tap-highlight-color:transparent}
.tip-dot:hover,.tip-dot.active{background:#58a6ff;color:#fff}
.tip-bubble{display:none;position:absolute;bottom:calc(100% + 8px);left:50%;transform:translateX(-50%);background:#1f2937;color:#c9d1d9;font-size:0.72rem;padding:6px 10px;border-radius:6px;white-space:nowrap;z-index:200;box-shadow:0 4px 12px rgba(0,0,0,0.5);pointer-events:none}
.tip-bubble::after{content:'';position:absolute;top:100%;left:50%;transform:translateX(-50%);border:5px solid transparent;border-top-color:#1f2937}
.tip-dot.active .tip-bubble,.tip-dot:hover .tip-bubble{display:block}
@media(hover:none){.tip-dot:hover .tip-bubble{display:none}}
@media(hover:none){.tip-dot.active .tip-bubble{display:block}}
table{width:100%;border-collapse:collapse;font-size:0.82rem;table-layout:fixed}
th{text-align:left;padding:5px 8px;border-bottom:1px solid #30363d;color:#8b949e;font-weight:600}
td{padding:5px 8px;border-bottom:1px solid #21262d}
.up{color:#ef4444;font-weight:600}
.down{color:#22c55e;font-weight:600}
.pos-example{background:#161b22;border:1px solid #30363d;border-radius:6px;padding:10px;margin:8px 0}
.pos-split{display:flex;gap:6px;margin:6px 0;flex-wrap:wrap}
.pos-split>div{background:#21262d;border-radius:4px;padding:6px 10px;font-size:0.8rem;text-align:center;flex:1;min-width:80px}
.pos-timeline{display:flex;gap:4px;margin:8px 0;flex-wrap:wrap}
.pos-timeline>div{background:#0c2240;border:1px solid #1f3a5f;border-radius:4px;padding:4px 8px;font-size:0.75rem;flex:1;min-width:100px}
.pos-timeline>div>span{display:block;color:#8b949e;font-size:0.65rem}
.pos-timeline>div>b{color:#f0f6fc;font-size:0.75rem}
.footer{text-align:center;color:#8b949e;font-size:0.75rem;padding:16px 0;border-top:1px solid #21262d;margin-top:16px}
.chart-box{background:#0d1117;border:1px solid #21262d;border-radius:6px;padding:8px;margin:8px 0}
.ghost{color:#8b949e;font-size:0.78rem}
.glossary{margin-top:12px}
.glossary-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(290px,1fr));gap:8px;margin-top:6px}
.glossary-item{background:#21262d;border:1px solid #30363d;border-radius:6px;padding:8px 10px}
.glossary-item .term{color:#58a6ff;font-weight:600;font-size:0.85rem}
.glossary-item .desc{color:#c9d1d9;font-size:0.78rem;margin-top:3px;line-height:1.5}
.glossary-group{color:#8b949e;font-size:0.8rem;margin:10px 0 4px;border-left:3px solid #58a6ff;padding-left:8px;font-weight:600}
@media(max-width:768px){.glossary-grid{grid-template-columns:1fr}}
.navbar{position:sticky;top:0;z-index:100;background:#0d1117;border-bottom:1px solid #30363d;display:flex;overflow-x:auto;white-space:nowrap;margin:0 -16px 12px;padding:0 16px;scrollbar-width:thin;scrollbar-color:#30363d transparent}
@media(max-width:1100px){.navbar{margin:0 -10px 10px;padding:0 10px}}
.navbar::-webkit-scrollbar{height:3px}
.navbar::-webkit-scrollbar-track{background:transparent}
.navbar::-webkit-scrollbar-thumb{background:#30363d;border-radius:2px}
.navbar a{display:inline-block;padding:7px 11px;font-size:0.76rem;color:#8b949e;text-decoration:none;border-bottom:2px solid transparent;transition:color 0.15s,border-color 0.15s;flex-shrink:0;cursor:pointer}
.navbar a:hover{color:#c9d1d9}
.navbar a.active{color:#58a6ff;border-bottom-color:#58a6ff}
.table-wrap{overflow-x:auto;-webkit-overflow-scrolling:touch}
@media(max-width:768px){
  h1{font-size:1.2rem}
  table{font-size:0.75rem}
  th,td{padding:4px 6px}
  .beginner-box{font-size:0.76rem;padding:6px 10px}
}
@media(max-width:480px){
  body{padding:8px}
  h1{font-size:1.05rem;margin:6px 0}
  .card{padding:10px;margin-bottom:8px}
  .navbar{margin:0 -8px 8px;padding:0 8px}
  .navbar a{padding:8px 8px;font-size:0.7rem}
  .beginner-signal{gap:4px;margin:6px 0}
  .beginner-signal>div{min-width:85px;padding:3px 6px}
  .beginner-signal>div>span{font-size:0.6rem}
  .beginner-signal>div>b{font-size:0.75rem}
  .pos-split>div{min-width:70px;font-size:0.72rem;padding:4px 6px}
  .pos-timeline>div{min-width:85px;font-size:0.68rem;padding:3px 6px}
  .pos-timeline>div>span{font-size:0.56rem}
  .pos-timeline>div>b{font-size:0.68rem}
  table{font-size:0.7rem}
  th,td{padding:3px 5px}
  .beginner-box{font-size:0.72rem;padding:5px 8px}
  .glossary-item{padding:6px 8px}
  .glossary-item .term{font-size:0.78rem}
  .glossary-item .desc{font-size:0.7rem}
  .glossary-group{font-size:0.72rem}
}
@media(max-width:360px){
  body{padding:6px}
  h1{font-size:0.95rem}
  .card{padding:8px}
  .navbar a{padding:6px 6px;font-size:0.65rem}
  .beginner-signal>div{min-width:75px}
  .pos-split>div{min-width:60px}
  .pos-timeline>div{min-width:75px;font-size:0.62rem}
  table{font-size:0.65rem}
}

/* ===== Professional market terminal theme ===== */
:root{
  --bg:#08101f;--bg-deep:#060b16;--panel:#101a2b;--panel-2:#142136;
  --line:#22324a;--line-soft:#19283d;--text:#dce6f3;--muted:#8291a8;
  --primary:#60a5fa;--primary-soft:#162d4d;--up:#f25f68;--down:#28c780;
  --warn:#f5b94c;--shadow:0 16px 40px rgba(0,0,0,.22)
}
html{scroll-behavior:smooth;background:var(--bg-deep)}
body{
  background:
    radial-gradient(circle at 78% -10%,rgba(37,99,235,.18),transparent 32rem),
    linear-gradient(180deg,var(--bg-deep),var(--bg));
  color:var(--text);font-family:Inter,"PingFang SC","Microsoft YaHei",-apple-system,
  BlinkMacSystemFont,"Segoe UI",sans-serif;font-variant-numeric:tabular-nums;
  letter-spacing:.01em;max-width:1460px;padding:26px 28px 32px
}
.app-header{padding:12px 2px 18px;border-bottom:1px solid var(--line-soft);margin-bottom:14px}
.eyebrow{color:var(--primary);font-size:.68rem;font-weight:700;letter-spacing:.18em;margin-bottom:7px}
.title-row{display:flex;align-items:center;gap:12px;flex-wrap:wrap}
.title-row h1{font-size:1.85rem;line-height:1.15;text-align:left;margin:0;color:#f8fbff;letter-spacing:-.03em}
.app-header p{color:var(--muted);font-size:.78rem;margin-top:8px}
.app-header p span{color:#a9b8cb}
.data-badge{font-family:ui-monospace,SFMono-Regular,Consolas,monospace;font-size:.58rem;
  letter-spacing:.08em;color:#9cc8ff;background:rgba(37,99,235,.14);border:1px solid rgba(96,165,250,.35);
  border-radius:999px;padding:4px 8px}
.layout{gap:16px}
.card{position:relative;overflow:hidden;background:linear-gradient(145deg,rgba(18,30,49,.98),rgba(13,24,40,.98));
  border:1px solid var(--line);border-radius:13px;padding:18px;box-shadow:0 1px 0 rgba(255,255,255,.025);
  transition:border-color .18s ease,transform .18s ease,box-shadow .18s ease}
.card::before{content:"";position:absolute;inset:0 auto 0 0;width:2px;background:transparent}
.card:hover{border-color:#314766;box-shadow:var(--shadow);transform:translateY(-1px)}
.card:hover::before{background:linear-gradient(180deg,var(--primary),transparent 70%)}
.hero-card{background:linear-gradient(120deg,rgba(20,40,68,.98),rgba(13,26,46,.98));
  border-color:#2a456a;padding:22px 24px}
.hero-card::after{content:"";position:absolute;width:220px;height:220px;border-radius:50%;right:-90px;top:-130px;
  background:rgba(59,130,246,.13);filter:blur(2px);pointer-events:none}
.hero-card>p{font-size:1rem;line-height:1.9;max-width:1100px;color:#cbd8e8}
h2{display:flex;align-items:center;gap:8px;font-size:.98rem;letter-spacing:.01em;color:#dfeaff;
  margin:0 0 12px;padding-bottom:10px;border-bottom:1px solid var(--line-soft)}
h2::before{content:"";display:inline-block;width:3px;height:14px;border-radius:2px;background:var(--primary);box-shadow:0 0 12px rgba(96,165,250,.45)}
h3{color:#a7b6ca;font-size:.78rem;letter-spacing:.04em;text-transform:uppercase}
.market-strip{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:10px;margin:0 0 16px}
.market-strip>div{position:relative;min-width:0;background:linear-gradient(145deg,var(--panel-2),#101b2e);
  border:1px solid var(--line);border-radius:11px;padding:11px 12px;text-align:left;box-shadow:0 8px 20px rgba(0,0,0,.12)}
.market-strip>div::after{content:"";position:absolute;right:11px;top:11px;width:5px;height:5px;border-radius:50%;background:#334b6c}
.market-strip>div>span{font-size:.66rem;color:var(--muted);margin-bottom:5px;letter-spacing:.03em}
.market-strip>div>b{font-family:ui-monospace,SFMono-Regular,Consolas,"Roboto Mono",monospace;font-size:.9rem;color:#f5f9ff}
.beginner-box{background:linear-gradient(90deg,rgba(27,58,96,.76),rgba(18,39,67,.64));
  border:1px solid rgba(96,165,250,.22);border-left:3px solid var(--primary);border-radius:7px;
  padding:10px 12px;color:#b9c8db}
.beginner-box b{color:#e8f1fd}
.beginner-box .action{color:#7fb5f5;font-weight:500;padding-top:4px;border-top:1px solid rgba(96,165,250,.12)}
table{font-size:.79rem}
th{padding:8px 9px;color:#718198;font-size:.68rem;text-transform:uppercase;letter-spacing:.05em;
  border-bottom:1px solid var(--line);background:rgba(7,15,27,.28)}
td{padding:8px 9px;border-bottom:1px solid var(--line-soft);color:#bfcbdb}
tbody tr{transition:background .15s ease}
tbody tr:hover{background:rgba(96,165,250,.045)}
td:nth-child(n+2){font-family:ui-monospace,SFMono-Regular,Consolas,"Roboto Mono",monospace}
.up{color:var(--up)}.down{color:var(--down)}
.chart-box{background:linear-gradient(180deg,#09111f,#080f1b);border:1px solid var(--line-soft);border-radius:9px;
  padding:10px;margin:12px 0;box-shadow:inset 0 1px 0 rgba(255,255,255,.02)}
.chart-box svg>rect:first-child{fill:#09111f}
.card[data-span="2"] .chart-box{width:100%;max-width:calc((100% - 16px)/2);align-self:center}
.ghost{color:var(--muted)}
.glossary{background:linear-gradient(145deg,#101a2b,#0d1828)}
.glossary-grid{gap:10px}
.glossary-item{background:rgba(20,33,54,.72);border-color:var(--line);border-radius:9px;padding:11px 12px}
.glossary-item .term{color:#9cc8ff}.glossary-item .desc{color:#aebdd0}
.glossary-group{color:#91a1b7;border-left-color:var(--primary);letter-spacing:.05em}
.footer{color:#687991;border-top-color:var(--line-soft);padding-top:22px}
.tip-dot{background:#263650;color:#96a7bc}.tip-dot:hover,.tip-dot.active{background:var(--primary)}
.tip-bubble{background:#17253a;color:#d4dfed;border:1px solid var(--line)}

@media(min-width:1200px){
  body{padding-left:220px}
  .navbar{position:fixed;left:max(18px,calc((100vw - 1460px)/2));top:28px;width:174px;height:calc(100vh - 56px);
    flex-direction:column;align-items:stretch;overflow-y:auto;overflow-x:hidden;margin:0;padding:12px 9px;
    background:rgba(10,18,32,.9);backdrop-filter:blur(16px);border:1px solid var(--line);border-radius:13px;
    box-shadow:var(--shadow)}
  .navbar::before{content:"REPORT SECTIONS";display:block;color:#5f7087;font-size:.56rem;font-weight:700;
    letter-spacing:.13em;padding:5px 9px 10px}
  .navbar a{position:relative;width:100%;border:0;border-radius:7px;padding:8px 10px;font-size:.7rem}
  .navbar a:hover{background:rgba(96,165,250,.07)}
  .navbar a.active{color:#dcecff;background:rgba(37,99,235,.16);box-shadow:inset 2px 0 0 var(--primary)}
}

@media(max-width:1199px){
  body{max-width:100%;padding:18px}
  .navbar{top:0;margin:0 -18px 14px;padding:7px 18px;background:rgba(8,16,31,.92);backdrop-filter:blur(14px);
    border-top:1px solid rgba(255,255,255,.025);border-bottom:1px solid var(--line)}
  .navbar a{border:1px solid transparent;border-radius:999px;padding:6px 10px;margin-right:3px}
  .navbar a.active{background:rgba(37,99,235,.16);border-color:rgba(96,165,250,.25)}
}

@media(max-width:1100px){
  .card[data-span="2"] .chart-box{max-width:none}
}

@media(max-width:760px){
  body{padding:12px}
  .app-header{padding:8px 1px 14px}.title-row h1{font-size:1.42rem}.app-header p{font-size:.7rem}
  .market-strip{grid-template-columns:1fr 1fr;gap:7px}
  .market-strip>div{padding:9px 10px}.market-strip>div:last-child{grid-column:1/-1}
  .layout{gap:10px}.card{padding:14px;border-radius:10px}.hero-card{padding:17px}
  .hero-card>p{font-size:.86rem;line-height:1.75}
  .navbar{margin:0 -12px 11px;padding:6px 12px}.navbar a{font-size:.67rem;padding:5px 9px}
  table{display:table;width:100%;table-layout:fixed;overflow:visible;white-space:normal;font-size:.72rem}
  th,td{min-width:0;padding:7px 6px;white-space:normal;overflow-wrap:anywhere;word-break:break-word;line-height:1.45}
  .chart-box{padding:5px;margin:9px 0}.beginner-box{font-size:.73rem;padding:8px 9px}
}

@media(max-width:390px){
  body{padding:9px}.eyebrow{font-size:.56rem}.title-row h1{font-size:1.22rem}.data-badge{font-size:.5rem}
  .app-header p{line-height:1.5}.navbar{margin:0 -9px 9px;padding:5px 9px}
  .market-strip>div>b{font-size:.78rem}.card{padding:12px}h2{font-size:.9rem}
}
"""

JS = """
function buildNav(){
var nav=document.getElementById('navbar');
if(!nav)return;
var overrides={'量能与资金面':'量能资金','领涨与领跌':'领涨领跌','技术条件观察':'技术观察','指数相对强弱':'RS强弱','大盘位置与支撑/压力':'大盘位置'};
var cards=document.querySelectorAll('.card');
var items=[];
for(var i=0;i<cards.length;i++){
var h2=cards[i].querySelector('h2');
if(!h2)continue;
var clone=h2.cloneNode(true);
var spans=clone.querySelectorAll('span');
for(var j=0;j<spans.length;j++)spans[j].remove();
var raw=clone.textContent.trim();
var cn=raw.replace(/\\s+[A-Za-z;].*/,'').trim();
if(/[：:]/.test(cn))cn=cn.split(/[：:]/)[0];
var label=overrides[raw]||overrides[cn]||cn;
if(label.length>5)label=label.substring(0,5);
var id='sec-'+i;
cards[i].setAttribute('id',id);
items.push('<a href="#'+id+'" data-target="'+id+'">'+label+'</a>');
}
nav.innerHTML=items.join('');
var links=nav.querySelectorAll('a');
for(var k=0;k<links.length;k++){
links[k].addEventListener('click',function(e){
e.preventDefault();
var t=document.getElementById(this.getAttribute('data-target'));
if(t)t.scrollIntoView({behavior:'smooth',block:'start'});
});
}
var timer=null;
function highlight(){
var sy=window.scrollY+80;
var cur=null;
for(var m=0;m<cards.length;m++){
if(cards[m].offsetTop<=sy)cur=cards[m];
}
// 修复：滚到顶部时所有 section 都不在识别线下方，cur 为空——强制高亮第一个，避免高亮卡在"风险面"等中间 section
if(!cur&&cards[0])cur=cards[0];
if(cur){
for(var n=0;n<links.length;n++){
if(links[n].getAttribute('data-target')===cur.id){links[n].classList.add('active');}
else{links[n].classList.remove('active');}
}
// 滚动导航栏让当前项可见
for(var p=0;p<links.length;p++){
if(links[p].classList.contains('active')){
var nl=links[p].offsetLeft,nr=nl+links[p].offsetWidth;
if(nl<nav.scrollLeft||nr>nav.scrollLeft+nav.clientWidth){
nav.scrollTo({left:nl-20,behavior:'smooth'});
}
}
}
}
}
window.addEventListener('scroll',function(){
if(timer)clearTimeout(timer);
timer=setTimeout(highlight,50);
});
highlight();
// 将卡片中 H2 之后、小白速读之前的内容包入 card-body，使相邻卡片图表在同一水平
for(var r=0;r<cards.length;r++){
var c=cards[r];
var h2=c.querySelector('h2');
var bb=c.querySelector('.beginner-box');
if(!h2)continue;
var body=document.createElement('div');
body.className='card-body';
var el=h2.nextElementSibling;
while(el&&el!==bb){
var next=el.nextElementSibling;
body.appendChild(el);
el=next;
}
h2.insertAdjacentElement('afterend',body);
}
// 表格包裹 div 实现移动端横向滚动
var tbls=document.querySelectorAll('table');
for(var q=0;q<tbls.length;q++){
if(tbls[q].parentElement.classList.contains('table-wrap'))continue;
var tw=document.createElement('div');
tw.className='table-wrap';
tbls[q].parentNode.insertBefore(tw,tbls[q]);
tw.appendChild(tbls[q]);
}
// 提示气泡：点击显示，点击外部关闭（H5兼容）
var tips=document.querySelectorAll('.tip-dot');
for(var u=0;u<tips.length;u++){
tips[u].addEventListener('click',function(e){
e.stopPropagation();
var was=this.classList.contains('active');
// 关闭所有
for(var v=0;v<tips.length;v++)tips[v].classList.remove('active');
// 如果之前没开就打开
if(!was)this.classList.add('active');
});
}
document.addEventListener('click',function(){
for(var w=0;w<tips.length;w++)tips[w].classList.remove('active');
});
}
if(document.readyState==='loading'){document.addEventListener('DOMContentLoaded',buildNav);}
else{buildNav();}
"""

# ========== HTML 生成 ==========

# 术语速查：分组 -> [(术语, 大白话解释)]
GLOSSARY = [
    ("均线篇", [
        ("三日线", "最近3天收盘价的平均线，最敏感的短线指标，跌破=短线走弱，站上=短线偏强"),
        ("五日线", "最近5天收盘价平均，短线「生死线」，股价在上方=短线多头，跌破要警惕"),
        ("十日线", "半月线，短中线过渡参考，主力常以此为短线防守位"),
        ("二十日线", "最近20个交易日收盘价均值，常用于观察中期价格位置，不直接等同于买卖信号"),
        ("六十日线", "季线，中线「生命线」，跌破通常意味着中期调整开始"),
    ]),
    ("技术指标篇", [
        ("MACD", "看趋势的指标。金叉(DIF上穿DEA)看涨、死叉看跌；红柱放大=多头增强，绿柱放大=空头增强"),
        ("KDJ", "看超买超卖。J值>100=超买(涨太快)、J<0=超卖(跌过头)；超买不一定马上跌，但短线风险大"),
        ("RSI", "强弱指标。>70偏强、<30偏弱；6日版更灵敏，14日版更稳"),
        ("布林带", "上中下三轨。触上轨=偏强、触下轨=偏弱；轨道收口=即将变盘(要选方向)"),
        ("量比", "今日成交÷近期平均。>1=放量、<1=缩量、>2=剧烈放量；放量上涨才靠谱"),
    ]),
    ("操作手法篇", [
        ("做T", "日内高抛低吸：同一天先卖后买(或先买后卖)，利用日内波动降低持仓成本，不改变总仓位"),
        ("金叉/死叉", "快线(短期)上穿慢线(长期)=金叉(看涨)；下穿=死叉(看跌)。MACD/KDJ/均线都可用"),
        ("超买/超卖", "涨/跌过头了。超买=短期可能回调，超卖=短期可能反弹；注意是「可能」不是「一定」"),
        ("破位/反抽", "价格跌破观察线常称破位；随后回到观察线附近常称反抽，均需结合其他数据判断"),
        ("连板", "连续涨停。2连板=连续2天涨停，「连板高度」=连板天数，高度越高情绪越亢奋"),
        ("打板", "在涨停价买入，赌次日继续涨(溢价)。高风险手法，封板失败=当日被套"),
        ("顶背离/底背离", "价格创新高/新低但指标不跟。顶背离=见顶预警、底背离=见底预警，是反转的前兆信号"),
    ]),
    ("资金情绪篇", [
        ("主力净流入", "westock 返回的资金净流入统计字段；正负表示该统计口径下的净额，不足以证明特定主体行为"),
        ("超大单", "按成交额阈值划分的大额订单分类，不能据此确认交易者身份或未来方向"),
        ("涨停/跌停", "当日涨/跌到限制价。主板±10%、创业板/科创板±20%、ST股±5%；封死涨停=买盘极强"),
        ("龙头", "板块里最强的领涨票，往往连板高度最高、资金最集中；龙头不死板块不倒"),
        ("情绪温度", "涨家数vs跌家数、涨停家数综合判断。涨停>50家=偏热、涨停<20家=偏冷；冰点反而易反弹"),
    ]),
]

def glossary_html():
    parts = ['<div class="card glossary" data-span="2">',
             '<h2>术语速查 <span class="ghost" style="font-size:0.75rem;font-weight:400">看不懂的词查这里</span></h2>']
    for group_title, terms in GLOSSARY:
        parts.append(f'<div class="glossary-group">{group_title}</div>')
        parts.append('<div class="glossary-grid">')
        for cn, desc in terms:
            parts.append(f'<div class="glossary-item"><span class="term">{cn}</span><div class="desc">{desc}</div></div>')
        parts.append('</div>')
    parts.append('</div>')
    return "\n".join(parts)

def generate_html(a):
    d = a["date"]; sh = a["sh"]; gz = a["gz"]
    market_state = "上涨" if sh.get("change_percent",0) > 0 else "下跌" if sh.get("change_percent",0) < 0 else "平盘"
    trend_short = "连涨偏强" if a["is_golden"] and a["is_above_ma5"] else "偏弱"
    overbought = f"是(J={f2(a['j_val'])}>100)⚠️" if a["is_overbought"] else f"否(J={f2(a['j_val'])}≤100)"
    money_signal = "放量" if a["money_60d_ratio"] > 100 else "缩量"

    sector_rows = "".join(
        f'<tr><td>{s.get("name","")}</td><td class="up">{s.get("changePct","")}%</td><td>{s.get("changePct5d","--")}%</td><td>{s.get("leadStock","--")}</td></tr>'
        for s in a["top_sectors"][:5]
    )
    concept_rows = "".join(
        f'<tr><td>{c.get("name","")}</td><td class="up">{c.get("changePct","")}%</td><td>{c.get("changePct5d","--")}%</td><td>{c.get("leadStock","--")}</td></tr>'
        for c in a["concept_top"][:6]
    )
    streak_rows = "".join(
        f'<tr><td>{s.get("LimitUpDays","")}板</td><td>{s.get("名称","")}</td><td>{fmt_code(s.get("代码",""))}</td></tr>'
        for s in a["top_streaks"][:5]
    )

    risk_beginner = f"KDJ的J值是{f2(a['j_val'])}，{'超过100表示近期上涨速度偏快，短线波动可能加大' if a['is_overbought'] else '没有超过100，暂未进入常用的超买区间'}。MACD{'金叉表示短期动能正在增强' if a['is_golden'] else '死叉表示短期动能偏弱'}，当前价格{'站在' if a['is_above_ma20'] else '落在'}20日均线{'上方' if a['is_above_ma20'] else '下方'}。"
    risk_action = "把它理解成市场体温计：反映当前状态，不代表接下来一定上涨或下跌"
    attack_beginner = f"国证2000今天{fp(gz.get('change_percent',0))}，近5日累计{fp(gz.get('chg_5d',0))}。{'KDJ已经超过100，说明小盘股短期涨速较快' if a['gz_j'] > 100 else 'KDJ未进入超买区间'}。"
    attack_action = "国证2000偏向小盘股，可用来观察小盘方向是否比大盘更活跃"
    emotion_beginner = f"{a['up_count']}只涨/{a['down_count']}只跌，涨停{a['up_limit']}家跌停{a['down_limit']}家。成交{fa(a['money_yi'])}。"
    emotion_action = "上涨家数多于下跌家数，通常表示多数股票表现较强；反过来则说明赚钱效应偏弱。数据来自涨跌分布接口"

    limit_beginner = f"收盘涨停{a['up_limit']}家、跌停{a['down_limit']}家，统一来自涨跌分布接口。"
    limit_action = "接口未提供同口径的触板数，因此不计算封板率或炸板率"

    # 市场宽度小白速读
    w = a['width_scores']
    nh = a['new_highs']; nl = a['new_lows']
    width_beginner = f"创新高{nh.get(60,0)}只 vs 创新低{nl.get(60,0)}只，{w['stock_width'][1]}。"
    width_action = "新高明显多于新低，说明上涨不是只靠少数权重股；新低增多则表示市场内部走弱"

    # 主力资金小白速读
    mf = a['main_force_top']
    if mf:
        mf_beginner = f"主力今日净买入最多的是{mf[0]['name']}({mf[0]['net']:+.2f}亿)，TOP10合计{sum(s['net'] for s in mf):+.1f}亿。"
        mf_action = "净流入是资金统计口径，不等于已经确认某家机构买入，也不能单独预测后续涨跌"
    else:
        mf_beginner = "暂无主力资金数据"
        mf_action = ""

    period_rows = (
        f'<tr><td>日线</td><td class="{"up" if a["daily_trend"]=="多头" else "down"}">{a["daily_trend"]}</td></tr>'
        f'<tr><td>周线</td><td class="{"up" if a["weekly_trend"]=="多头" else "down"}">{a["weekly_trend"]}</td></tr>'
        f'<tr><td>月线</td><td class="{"up" if a["monthly_trend"]=="多头" else "down"}">{a["monthly_trend"]}</td></tr>'
    )

    s0 = a["top_sectors"][0] if a["top_sectors"] else {}
    s1 = a["top_sectors"][1] if len(a["top_sectors"]) > 1 else {}
    c0 = a["concept_top"][0] if a["concept_top"] else {}
    c1 = a["concept_top"][1] if len(a["concept_top"]) > 1 else {}
    s2 = a["top_sectors"][2] if len(a["top_sectors"]) > 2 else {}

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0,maximum-scale=5.0">
<title>A股每日技术复盘 {d}</title>
<style>{CSS}</style>
</head>
<body>
<header class="app-header">
<div class="eyebrow">MARKET INTELLIGENCE · DAILY REVIEW</div>
<div class="title-row"><h1>A股每日技术复盘</h1><span class="data-badge">WESTOCK VERIFIED</span></div>
<p>收盘后的指数、技术、情绪与资金全景 · <span>{d}</span></p>
</header>
<nav class="navbar" id="navbar"></nav>

<div class="beginner-signal market-strip">
<div><span>上证当日状态</span><b>{market_state}</b></div>
<div><span>短期趋势<span class="tip-dot">?<span class="tip-bubble">金叉+站上MA5=偏强，否则偏弱</span></span></span><b>{trend_short}</b></div>
<div><span>是否超买<span class="tip-dot">?<span class="tip-bubble">KDJ的J值&gt;100即超买，涨太快有回调风险</span></span></span><b>{overbought}</b></div>
<div><span>量能信号<span class="tip-dot">?<span class="tip-bubble">对比60日均量，&gt;100%=放量，&lt;100%=缩量</span></span></span><b>{money_signal}</b></div>
<div><span>技术条件满足度<span class="tip-dot">?<span class="tip-bubble">项目汇总6项条件：MACD金叉、站上MA5、站上MA20、上证上涨、国证2000上涨、MACD柱为正；不是westock原生指标，也不预测后续涨跌</span></span></span><b>{a['bull_score']}/6 · {a['signal_label']}</b></div>
</div>

<div class="layout" id="main">

<!-- ====== 大盘总览 ====== -->

<div class="card hero-card" data-span="2">
<h2>首屏结论</h2>
<p>上证收<b class="{'up' if sh.get('change_percent',0)>0 else 'down'}">{f2(sh.get('price',0))}</b>({fp(sh.get('change_percent',0))})，国证2000收<b class="{'up' if gz.get('change_percent',0)>0 else 'down'}">{f2(gz.get('price',0))}</b>({fp(gz.get('change_percent',0))})。六项技术条件满足<b>{a['bull_score']}</b>项，综合状态为<b>{a['signal_label']}</b>。该结论为规则化指标摘要，不是仓位或买卖指令。</p>
<div class="beginner-box"><b>小白速读：</b>{risk_beginner}<span class="action">{risk_action}</span></div>
</div>

<div class="card">
<h2>风险面：上证指数</h2>
<table>
<tr><th>指标</th><th>数值</th><th>信号</th></tr>
<tr><td>收盘价</td><td class="{'up' if sh.get('change_percent',0)>0 else 'down'}">{f2(sh.get('price',0))}</td><td>{fp(sh.get('change_percent',0))}</td></tr>
<tr><td>MACD DIF/DEA</td><td>{f2(a['dif'])} / {f2(a['dea'])}</td><td class="{'up' if a['is_golden'] else 'down'}">{'金叉' if a['is_golden'] else '死叉'} {'(水下)' if not a['macd_above_zero'] else '(水上)'}</td></tr>
<tr><td>MACD柱</td><td class="{'up' if a['macd_val']>0 else 'down'}">{f2(a['macd_val'])}</td><td>{'红柱放大' if a['macd_val']>0 else '绿柱'}</td></tr>
<tr><td>KDJ K/D/J</td><td>{f2(a['k_val'])} / {f2(a['d_val'])} / {f2(a['j_val'])}</td><td class="{'down' if a['is_overbought'] else 'up'}">{'超买⚠️' if a['is_overbought'] else '正常'}</td></tr>
<tr><td>RSI(6)</td><td>{f2(a['rsi6'])}</td><td>{'偏强' if a['rsi6']>70 else '中性'}</td></tr>
<tr><td>MA5/10/20</td><td>{f2(a['ma5'])} / {f2(a['ma10'])} / {f2(a['ma20'])}</td><td>{'站上均线' if a['is_above_ma5'] and a['is_above_ma20'] else '部分破位'}</td></tr>
<tr><td>MA60</td><td>{f2(a['ma60'])}</td><td class="{'down' if not a['is_above_ma60'] else 'up'}">{'线下(压力)' if not a['is_above_ma60'] else '线上'}</td></tr>
<tr><td>BOLL 上/中/下</td><td>{f2(a['boll_upper'])} / {f2(a['boll_mid'])} / {f2(a['boll_lower'])}</td><td>{'触及上轨' if sh.get('price',0)>a['boll_upper']*0.99 else '中轨上方' if sh.get('price',0)>a['boll_mid'] else '中轨下方'}</td></tr>
</table>
<div class="chart-box">{kline_svg(a['sh_daily'][:20][::-1] if a['sh_daily'] else [], '上证指数日K线')}</div>
<div class="beginner-box"><b>小白速读：</b>{risk_beginner}<span class="action">{risk_action}</span></div>
</div>

<div class="card">
<h2>进攻面：国证2000</h2>
<table>
<tr><th>指标</th><th>数值</th><th>信号</th></tr>
<tr><td>收盘价</td><td class="up">{f2(gz.get('price',0))}</td><td>{fp(gz.get('change_percent',0))}</td></tr>
<tr><td>5日涨幅</td><td class="up">{f2(gz.get('chg_5d',0))}%</td><td>vs上证{f2(sh.get('chg_5d',0))}%</td></tr>
<tr><td>MACD DIF/DEA</td><td>{f2(a['gz_dif'])} / {f2(a['gz_dea'])}</td><td class="up">金叉{'(水下)' if a['gz_dif']<0 else '(水上)'}</td></tr>
<tr><td>MACD柱</td><td class="up">{f2(a['gz_macd_val'])}</td><td>红柱</td></tr>
<tr><td>KDJ J</td><td class="{'down' if a['gz_j']>100 else 'up'}">{f2(a['gz_j'])}</td><td>{'超买⚠️' if a['gz_j']>100 else '正常'}</td></tr>
<tr><td>量比</td><td>{f2(gz.get('volume_ratio',0))}</td><td>{'放量' if gz.get('volume_ratio',0)>1 else '缩量'}</td></tr>
</table>
<div class="chart-box">{kline_svg(a['gz_daily'][:20][::-1] if a['gz_daily'] else [], '国证2000日K线')}</div>
<div class="beginner-box"><b>小白速读：</b>{attack_beginner}<span class="action">{attack_action}</span></div>
</div>

<!-- ====== 市场状态 ====== -->

<div class="card">
<h2>大盘位置与支撑/压力</h2>
<table>
<tr><th>级别</th><th>价格</th><th>依据</th></tr>
<tr><td>强压力</td><td class="down">{f2(a['ma60'])}</td><td>MA60/半年线</td></tr>
<tr><td>中压力</td><td class="down">{f2(a['boll_upper'])}</td><td>BOLL上轨</td></tr>
<tr><td style="font-weight:bold;color:#58a6ff">当前</td><td style="font-weight:bold">{f2(sh.get('price',0))}</td><td>{'连续阳线' if sh.get('change_percent',0)>0 else '调整中'}</td></tr>
<tr><td>中支撑</td><td class="up">{f2(a['ma20'])}</td><td>MA20/BOLL中轨</td></tr>
<tr><td>强支撑</td><td class="up">{f2(a['boll_lower'])}</td><td>BOLL下轨</td></tr>
</table>
<div class="beginner-box"><b>小白速读：</b>BOLL上轨{f2(a['boll_upper'])}可以理解为近期价格波动区间的上沿，MA20的{f2(a['ma20'])}是近20日平均价格。当前指数在两者之间{'偏上' if sh.get('price',0)>(a['boll_upper']+a['ma20'])/2 else '偏下'}。<span class="action">这些位置用于理解价格所处区域，不是自动买卖线</span></div>
</div>

<div class="card">
<h2>情绪面：全市场广度</h2>
<table>
<tr><th>指标</th><th>数值</th></tr>
<tr><td>上涨家数</td><td class="up">{a['up_count']}</td></tr>
<tr><td>下跌家数</td><td class="down">{a['down_count']}</td></tr>
<tr><td>涨停/跌停</td><td><span class="up">{a['up_limit']}</span> / <span class="down">{a['down_limit']}</span></td></tr>
<tr><td>两市成交额</td><td>{fa(a['money_yi'])}</td></tr>
<tr><td>5日均量比</td><td>{f2(a['trade'].get('MONEY_5DAVG_RATIO',0))}%</td></tr>
<tr><td>60日均量比</td><td class="{'down' if a['money_60d_ratio']<100 else 'up'}">{f2(a['money_60d_ratio'])}%</td></tr>
<tr><td>创60日新高</td><td>{a['high60']}</td></tr>
<tr><td>创60日新低</td><td>{a['low60']}</td></tr>
</table>
<div class="chart-box">{dist_svg(a['cd'])}</div>
<div class="beginner-box"><b>小白速读：</b>{emotion_beginner}<span class="action">{emotion_action}</span></div>
</div>

<div class="card">
<h2>市场宽度</h2>
<table>
<tr><th>维度</th><th>评分</th><th>状态</th></tr>
<tr><td>个股宽度</td><td>{a['width_scores']['stock_width'][0]}</td><td>{a['width_scores']['stock_width'][1]}</td></tr>
<tr><td>板块宽度</td><td>{a['width_scores']['sector_width'][0]}</td><td>{a['width_scores']['sector_width'][1]}</td></tr>
<tr><td>情绪温度</td><td>{a['width_scores']['sentiment'][0]}</td><td>{a['width_scores']['sentiment'][1]}</td></tr>
<tr><td>技术面</td><td>{a['width_scores']['tech'][0]}</td><td>{a['width_scores']['tech'][1]}</td></tr>
<tr><td>风格轮动</td><td>{a['width_scores']['style_rot'][0]}</td><td>{a['width_scores']['style_rot'][1]}</td></tr>
<tr><td>板块轮动</td><td>{a['width_scores']['sector_rot'][0]}</td><td>{a['width_scores']['sector_rot'][1]}</td></tr>
</table>
<div class="chart-box">{width_svg(a['new_highs'], a['new_lows'])}</div>
<div class="beginner-box"><b>小白速读：</b>{width_beginner}<span class="action">{width_action}</span></div>
</div>

<div class="card">
<h2>量能与资金面</h2>
<table>
<tr><th>指标</th><th>数值</th></tr>
<tr><td>当日成交额</td><td>{fa(a['money_yi'])}</td></tr>
<tr><td>5日均量</td><td>{fa(a['money_5d_avg'])}</td></tr>
<tr><td>60日均量</td><td>{fa(a['money_60d_avg'])}</td></tr>
<tr><td>量比(5日)</td><td>{f2(a['trade'].get('MONEY_5DAVG_RATIO',0))}%</td></tr>
<tr><td>量比(60日)</td><td class="{'down' if a['money_60d_ratio']<100 else 'up'}">{f2(a['money_60d_ratio'])}%</td></tr>
<tr><td>量价配合</td><td class="{'up' if a['vol_healthy'] else 'down'}">{'健康' if a['vol_healthy'] else '背离'}</td></tr>
</table>
<div class="chart-box">{vol_svg(a['sh_daily'])}</div>
<div class="beginner-box"><b>小白速读：</b>今天的成交额相当于60日平均水平的{f2(a['money_60d_ratio'])}%，也就是{'高于' if a['money_60d_ratio']>=100 else '低于'}长期平均量。<span class="action">成交量代表市场活跃程度，不能单独证明所谓“主力”正在买入或卖出</span></div>
</div>

<div class="card">
<h2>多周期共振</h2>
<table>
<tr><th>周期</th><th>方向</th></tr>
{period_rows}
</table>
<p class="ghost" style="margin-top:8px">{'短多中空，尚未全周期共振，属日线级别反弹' if a['daily_trend']!='偏空' and a['monthly_trend']=='空头' else '多周期共振偏多' if a['daily_trend']!='偏空' and a['weekly_trend']=='多头' else '多周期偏空，谨慎'}</p>
<div class="beginner-box"><b>小白速读：</b>日线看短期、周线看中期、60日方向看更长一段时间。当前三个周期可能给出不同方向，就像短期反弹不一定已经扭转长期趋势。<span class="action">周期越长，变化通常越慢；不要把单日上涨直接当成长期反转</span></div>
</div>

<div class="card">
<h2>指数相对强弱</h2>
<div class="chart-box">{rs_svg(sh, a['sz'], a['cyb'], a['zz1000'], gz)}</div>
</div>

<!-- ====== 短线情绪 ====== -->

<div class="card">
<h2>领涨与领跌</h2>
<h3>领涨行业</h3>
<table>
<tr><th>板块</th><th>涨幅</th><th>5日</th><th>领涨股</th></tr>
{sector_rows}
</table>
<h3>热门概念</h3>
<table>
<tr><th>概念</th><th>涨幅</th><th>5日</th><th>领涨股</th></tr>
{concept_rows}
</table>
<div class="beginner-box"><b>小白速读：</b>这里展示当天涨幅靠前的行业和概念，用来回答“今天资金主要在炒什么方向”。<span class="action">当天排名靠前只说明当日强势，不代表第二天还会继续上涨</span></div>
</div>

<div class="card">
<h2>连板梯队</h2>
<table>
<tr><th>高度</th><th>名称</th><th>代码</th></tr>
{streak_rows}
</table>
<div class="chart-box">{sector_svg(a['top_sectors'])}</div>
<div class="beginner-box"><b>小白速读：</b>最高{a['max_streak']}连板，意思是榜首股票已经连续{a['max_streak']}个交易日涨停；全市场今天收盘涨停{a['up_limit']}家。<span class="action">连板越高通常代表短线情绪越热，但价格波动和回撤风险也会更大</span></div>
</div>

<div class="card">
<h2>涨跌停统计</h2>
<table>
<tr><th>指标</th><th>数值</th><th>数据源</th></tr>
<tr><td>收盘涨停</td><td class="up">{a['up_limit']}</td><td>涨跌分布</td></tr>
<tr><td>收盘跌停</td><td class="down">{a['down_limit']}</td><td>涨跌分布</td></tr>
</table>
<div class="beginner-box"><b>小白速读：</b>{limit_beginner}涨停家数反映当天极强股票数量，跌停家数反映极弱股票数量。<span class="action">{limit_action}</span></div>
</div>

<div class="card" data-span="2">
<h2>主力资金动向</h2>
<table>
<tr><th>#</th><th>名称</th><th>代码</th><th>主力净流入(亿)</th></tr>
{''.join(f'<tr><td>{i+1}</td><td>{s["name"]}</td><td>{fmt_code(s["code"])}</td><td class="up">{s["net"]:+.2f}</td></tr>' for i,s in enumerate(a['main_force_top'][:10]))}
</table>
<div class="chart-box">{force_svg(a['main_force_top'])}</div>
<div class="beginner-box"><b>小白速读：</b>{mf_beginner}<span class="action">{mf_action}</span></div>
</div>

<!-- ====== 操作策略 ====== -->

<div class="card" data-span="2">
<h2>主线板块</h2>
<table>
<tr><th>级别</th><th>方向</th><th>逻辑</th></tr>
<tr><td class="up">P0</td><td>{s0.get('name','--')} + {c0.get('name','--')}</td><td>当日最强方向</td></tr>
<tr><td class="up">P1</td><td>{s1.get('name','--')} + {c1.get('name','--')}</td><td>5日涨幅领先</td></tr>
<tr><td>P2</td><td>{s2.get('name','--')}</td><td>跟涨方向</td></tr>
</table>
</div>

<div class="card" data-span="2">
<h2>技术条件观察</h2>
<table>
<tr><th>观察项</th><th>westock 当前值</th><th>用途</th></tr>
<tr><td>MA20</td><td>{f2(a['ma20'])}</td><td>比较当前指数位置</td></tr>
<tr><td>BOLL上轨</td><td>{f2(a['boll_upper'])}</td><td>观察价格是否接近上轨</td></tr>
<tr><td>MA60</td><td>{f2(a['ma60'])}</td><td>观察60日均线位置</td></tr>
<tr><td>MACD DIF / DEA</td><td>{f2(a['dif'])} / {f2(a['dea'])}</td><td>观察交叉状态</td></tr>
</table>
</div>

<div class="card">
<h2>数据与方法</h2>
<ul style="font-size:0.82rem;padding-left:20px">
<li>页面行情、K线、指标、板块与排行均来自本次 westock CLI 返回。</li>
<li>技术状态由页面列出的真实字段按固定规则计算，不补造缺失值。</li>
<li>任一必需文件、字段或 JSON 格式异常时，报告生成失败。</li>
<li>报告不提供仓位比例、资金分配或买卖指令。</li>
</ul>
</div>

<div class="card">
<h2>次日观察</h2>
<table>
<tr><th>观察项</th><th>本期真实基准</th><th>数据来源</th></tr>
<tr><td>上证5日均线</td><td>{f2(a['ma5'])}</td><td>市场总览</td></tr>
<tr><td>5日平均成交额</td><td>{fa(a['money_5d_avg'])}</td><td>市场总览</td></tr>
<tr><td>本期收盘涨停家数</td><td>{a['up_limit']}</td><td>涨跌分布</td></tr>
<tr><td>上证BOLL上轨</td><td>{f2(a['boll_upper'])}</td><td>市场总览</td></tr>
<tr><td>上证MA20</td><td>{f2(a['ma20'])}</td><td>市场总览</td></tr>
<tr><td>国证2000本期收盘</td><td>{f2(gz.get('price'))}</td><td>指数行情</td></tr>
</table>
</div>

<!-- ====== 附录 ====== -->

<div class="card" data-span="2">
<h2>风险提示</h2>
<ul style="font-size:0.82rem;padding-left:20px">
<li>以上内容是基于 westock 真实数据的规则化技术指标摘要，不构成投资建议。</li>
<li>技术指标存在滞后性，不能保证未来价格方向。</li>
<li>KDJ当前{'处于超买区间' if a['is_overbought'] else '未处于超买区间'}；60日均量比为{f2(a['money_60d_ratio'])}%。</li>
<li>日线、周线与60日方向应分别阅读，不将单一周期推断为确定结论。</li>
</ul>
</div>

</div>

{glossary_html()}

<div class="footer">
<p>A股每日技术复盘 | 统计日期：{d} | 自动生成(GitHub Actions)</p>
<p style="margin-top:4px">数据来源：westock-data / westock-tool | 缺失或异常数据会中止生成</p>
</div>

<script>{JS}</script>
</body>
</html>"""
    return html

# ========== 主函数 ==========
def main():
    today = datetime.now()
    force = "--force" in sys.argv or os.environ.get("FORCE_RUN") == "1"
    if today.weekday() >= 5 and not force:
        print("Weekend, skipping... (use --force to override)")
        sys.exit(0)

    try:
        data = load_all()
        validate_westock_data(data)
    except DataLoadError as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        sys.exit(1)

    a = analyze(data)

    # === 数据新鲜度校验 ===
    trade_date = a.get("date", "")
    if trade_date:
        from datetime import timedelta
        td = datetime.strptime(trade_date, "%Y-%m-%d")
        days_old = (today - td).days
        # 工作日运行：数据超过3天说明 API 可能返回了旧数据
        if days_old > 3 and not force:
            print(f"WARNING: Data is {days_old} days old (trade_date={trade_date}, today={today.strftime('%Y-%m-%d')})")
            print("         API may have returned stale data. Use --force to override.")
            sys.exit(1)
        elif days_old > 0:
            print(f"INFO: Using data from {trade_date} ({days_old} day(s) old, likely holiday)")
    else:
        trade_date = today.strftime("%Y-%m-%d")

    # === K线数据日期校验 ===
    sh_daily = data.get("sh_daily", [])
    if sh_daily:
        latest_kline_date = sh_daily[0].get("date", "")
        if latest_kline_date and latest_kline_date != trade_date:
            print(f"WARNING: K-line latest date ({latest_kline_date}) != trade date ({trade_date})")

    html = generate_html(a)

    trade_date_str = trade_date.replace("-", "")
    filename = f"技术面复盘_{trade_date_str}.html"
    filepath = os.path.join(ROOT_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)

    index_path = os.path.join(ROOT_DIR, "index.html")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Report generated: {filename}")
    print(f"Trade date: {trade_date}")

if __name__ == "__main__":
    main()

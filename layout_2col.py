#!/usr/bin/env python3
"""PC 端左右双栏布局改造：让 PC 上 section 左右分布，移动端保持单列。"""
import re
from pathlib import Path

HTML_PATH = Path(r"C:\Users\dhsq\WorkBuddy\AGU\daily-review\技术面复盘_20260807.html")

html = HTML_PATH.read_text(encoding="utf-8")

# ============================================================
# 1. CSS 改造
# ============================================================
# 1.1 body 宽度：从 920px → 1480px
old_body = 'body{background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"PingFang SC","Microsoft YaHei",sans-serif;line-height:1.6;font-size:14px;padding:20px;max-width:920px;margin:0 auto}'
new_body = 'body{background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"PingFang SC","Microsoft YaHei",sans-serif;line-height:1.6;font-size:14px;padding:20px 24px;max-width:1480px;margin:0 auto}'
assert old_body in html, "未找到目标 body 样式"
html = html.replace(old_body, new_body)

# 1.2 新增 PC 双栏样式（在 .lead-grid 定义后插入）
old_lead_end = '.lead-card li:last-child{border-bottom:none}'
new_lead_end = old_lead_end + '''
/* ===================== PC TWO-COLUMN LAYOUT ===================== */
.layout{display:block}
.row{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-bottom:20px}
.row>div{min-width:0;display:flex;flex-direction:column}
.row .section,.row .risk-warn{margin-bottom:0;height:100%}
.col-full{grid-column:1/-1}
@media(max-width:1100px){
.row{grid-template-columns:1fr;gap:16px}
.col-full{grid-column:auto}
}'''
assert old_lead_end in html
html = html.replace(old_lead_end, new_lead_end, 1)

# ============================================================
# 2. HTML 结构改造
# ============================================================
# 2.1 用 <div class="layout"> 包裹从 .tldr 到 .risk-warn 结束

# 找到 <div class="tldr"> 位置并在其前插入 <div class="layout">
tldr_open = '<div class="tldr">'
assert html.count(tldr_open) == 1
html = html.replace(tldr_open, '<div class="layout">\n<div class="layout-tldr">\n' + tldr_open, 1)

# 找到 </div>\n\n<div class="risk-warn"> - 在风险提示前关闭 tldr 容器
risk_warn_open = '<div class="risk-warn">'
assert html.count(risk_warn_open) == 1
html = html.replace(risk_warn_open, '</div>\n</div>\n\n<div class="risk-warn" data-span="2">', 1)

# 在 </div>\n\n<footer> 前关闭 layout（risk-warn 的闭合 + layout 闭合）
old_footer_pre = '</div>\n\n<footer>'
new_footer_pre = '</div>\n</div>\n\n<footer>'
assert old_footer_pre in html
html = html.replace(old_footer_pre, new_footer_pre, 1)

# 2.2 给需要全宽的 section 加 data-span="2"
# 主线板块
html = html.replace(
    '<h2><span class="cn-text">主线板块</span><span class="en-text">Main Themes</span></h2>',
    '<h2><span class="cn-text">主线板块</span><span class="en-text">Main Themes</span></h2>',
    1
)
# 找到主线板块 section 起始：上一行带 h2 的 div class="section"
# 因为风险面、进攻面、情绪面、大盘位置、量能、多周期 都是 .section，
# 主线板块是第7个 .section。简化：匹配"主线板块"h2前的 section 起始
old_main_theme_section = '<div class="section">\n<h2><span class="cn-text">主线板块</span>'
new_main_theme_section = '<div class="section" data-span="2">\n<h2><span class="cn-text">主线板块</span>'
assert old_main_theme_section in html, "未找到主线板块 section 起始"
html = html.replace(old_main_theme_section, new_main_theme_section, 1)

# 三档建仓参考
old_entry_section = '<div class="section">\n<h2><span class="cn-text">三档建仓参考</span>'
new_entry_section = '<div class="section" data-span="2">\n<h2><span class="cn-text">三档建仓参考</span>'
assert old_entry_section in html, "未找到三档建仓 section 起始"
html = html.replace(old_entry_section, new_entry_section, 1)

# ============================================================
# 3. JS 改造：在 function toggleLang() 前插入 DOMContentLoaded 重组逻辑
# ============================================================
js_init = '''<script>
document.addEventListener("DOMContentLoaded",function(){
  var layout=document.querySelector(".layout");
  if(!layout)return;
  var tldrWrap=layout.querySelector(".layout-tldr");
  var items=Array.prototype.slice.call(layout.querySelectorAll(".section,.risk-warn"));
  if(items.length===0)return;
  var wides=new Set();
  items.forEach(function(s,i){if(s.dataset.span==="2")wides.add(i);});
  var rows=[];
  var i=0;
  while(i<items.length){
    if(wides.has(i)){
      var r=document.createElement("div");r.className="row";
      var c=document.createElement("div");c.className="col-full";
      c.appendChild(items[i]);r.appendChild(c);rows.push(r);i++;
    }else if(i+1<items.length&&!wides.has(i+1)){
      var r2=document.createElement("div");r2.className="row";
      var c1=document.createElement("div");var c2=document.createElement("div");
      c1.appendChild(items[i]);c2.appendChild(items[i+1]);
      r2.appendChild(c1);r2.appendChild(c2);rows.push(r2);i+=2;
    }else{
      var r3=document.createElement("div");r3.className="row";
      var c3=document.createElement("div");
      c3.appendChild(items[i]);r3.appendChild(c3);rows.push(r3);i++;
    }
  }
  layout.innerHTML="";
  if(tldrWrap)layout.appendChild(tldrWrap);
  rows.forEach(function(r){layout.appendChild(r);});
});
'''

old_script_open = '<script>\nvar shKline=['
new_script_open = js_init + '\nvar shKline=['
assert old_script_open in html, "未找到 script 起始"
html = html.replace(old_script_open, new_script_open, 1)

# ============================================================
# 写回
# ============================================================
HTML_PATH.write_text(html, encoding="utf-8")
print(f"OK: {HTML_PATH}, size={len(html)} bytes")

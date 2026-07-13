""" HTML 报告生成 """

from collections import Counter
from pathlib import Path

from visualization import gen_heatmap, gen_weapon_chart, gen_player_chart, \
    gen_distance_chart, gen_player_heatmap


def generate_html(data, coach_data, llm_response, player_name, player_sid, output_path):
    """生成完整 HTML 报告，所有图片内嵌为 base64."""
    hi = gen_heatmap(data)
    wi = gen_weapon_chart(data)
    si = gen_player_chart(data)
    di = gen_distance_chart(data)
    phi = gen_player_heatmap(data, player_sid)

    # LLM 分析区块
    if llm_response:
        safe = llm_response.replace("&", "&amp;").replace("<", "&lt;") \
                           .replace(">", "&gt;").replace("\n", "<br>")
        llm_html = f"""<div class="card">
<h2>AI 教练分析 — {player_name}</h2>
<div style="background:#16213e;border-radius:10px;padding:16px;margin-top:8px;
     border-left:3px solid #FFD700;font-size:14px;line-height:1.8;">
{safe}
</div>
</div>"""
    else:
        llm_html = """<div class="card">
<h2>AI 教练分析</h2>
<div style="color:#888;font-size:13px;padding:12px;">
请在 config.py 中配置 LLM_API_KEY。
</div>
</div>"""

    # 自动分析摘要
    d2 = coach_data
    findings = []
    if d2["hs_pct"] < 40:
        findings.append(("枪法", f"爆头率 {d2['hs_pct']}%", "偏低，建议多练 prefire"))
    close_pct = round(d2["close"] / max(d2["kills"], 1) * 100, 1)
    long_pct = round(d2["long"] / max(d2["kills"], 1) * 100, 1)
    if long_pct > 40 and close_pct < 20:
        findings.append(("走位", f"远程 {long_pct}%", "可尝试更激进"))
    if d2["utility_kills"] == 0:
        findings.append(("道具", "0 道具击杀", "建议学投掷路线"))

    fi_html = ""
    for cat, issue, sug in findings:
        fi_html += f"""<div style="background:#16213e;border-radius:8px;padding:12px;margin-bottom:8px;border-left:3px solid #e94560;">
<div style="display:flex;justify-content:space-between;margin-bottom:4px;">
<span style="color:#e94560;font-weight:600;">{cat}</span>
<span style="color:#aaa;font-size:12px;">{issue}</span>
</div>
<div style="color:#e0e0e0;font-size:13px;">{sug}</div>
</div>"""

    # 选手表
    players = sorted(data["player_stats"].values(), key=lambda p: p["kills"], reverse=True)
    rows = ""
    for p in players:
        hl = ' class="hm"' if player_name in p["name"] else ""
        tag = f'<span class="tag-t">T</span>' if p["team"] == 2 else f'<span class="tag-ct">CT</span>'
        rows += f"<tr{hl}><td>{p['name']}</td><td>{tag}</td><td>{p['kills']}</td><td>{p['deaths']}</td><td>{p['kd']}</td><td>{p['hs']}</td><td>{p['hs_pct']}%</td></tr>\n"

    html = f"""<!DOCTYPE html><html lang="zh-CN"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>CS2 Report — {Path(output_path).stem}</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{background:#0d0d1a;color:#e0e0e0;font-family:-apple-system,'Microsoft YaHei',sans-serif;padding:20px;}}
.c{{max-width:1200px;margin:0 auto;}}
.hdr{{text-align:center;padding:30px;background:linear-gradient(135deg,#1a1a2e,#16213e);border-radius:16px;margin-bottom:20px;border:1px solid #2a2a4e;}}
.hdr h1{{font-size:28px;}} .hdr .t{{color:#FFD700;}} .hdr .ct{{color:#4A90D9;}}
.hdr .meta{{color:#888;font-size:14px;}} .hdr .meta span{{margin:0 12px;}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:20px;}}
.grid-f{{grid-template-columns:1fr;}}
.card{{background:#1a1a2e;border-radius:12px;overflow:hidden;border:1px solid #2a2a4e;padding:16px;}}
.card h2{{font-size:16px;margin-bottom:12px;color:#aaa;}}
.card img{{width:100%;height:auto;display:block;}}
.sr{{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:12px;margin-bottom:20px;}}
.sb{{background:linear-gradient(135deg,#1a1a2e,#16213e);border-radius:10px;padding:16px;text-align:center;border:1px solid #2a2a4e;}}
.sb .n{{font-size:28px;font-weight:700;}} .sb .l{{font-size:12px;color:#888;margin-top:4px;}}
.sb.g .n{{color:#2ECC71;}} .sb.o .n{{color:#E67E22;}} .sb.r .n{{color:#e74c3c;}}
.sb.t2 .n{{color:#FFD700;}} .sb.t3 .n{{color:#4A90D9;}}
.tbl{{width:100%;border-collapse:collapse;margin-top:8px;}}
.tbl th{{text-align:left;font-size:11px;color:#666;padding:6px 8px;border-bottom:1px solid #2a2a4e;}}
.tbl td{{padding:6px 8px;font-size:13px;border-bottom:1px solid #1a1a2e;}}
.tbl tr:hover{{background:rgba(255,255,255,0.03);}}
.tag-t,.tag-ct{{display:inline-block;padding:1px 6px;border-radius:4px;font-size:11px;font-weight:600;}}
.tag-t{{background:rgba(255,215,0,0.13);color:#FFD700;}}
.tag-ct{{background:rgba(74,144,217,0.13);color:#4A90D9;}}
.hm{{background:rgba(233,69,96,0.08)!important;font-weight:600;}}
.ft{{text-align:center;padding:20px;color:#555;font-size:12px;margin-top:30px;}}
@media(max-width:768px){{.grid{{grid-template-columns:1fr;}}}}
</style></head><body><div class="c">

<div class="hdr">
<h1><span class="t">CS2</span> Agent Report</h1>
<div class="meta"><span>MAP: {data['map_name']}</span>
<span>KILLS: {data['total_kills']}</span>
<span>ROUNDS: {data['total_rounds']}</span>
<span>PLAYERS: {data['total_players']}</span></div></div>

<div class="sr">
<div class="sb g"><div class="n">{d2['kills']}</div><div class="l">{d2['name']} 击杀</div></div>
<div class="sb r"><div class="n">{d2['deaths']}</div><div class="l">死亡</div></div>
<div class="sb o"><div class="n">{d2['kd']}</div><div class="l">K/D</div></div>
<div class="sb t2"><div class="n">{d2['hs_pct']}%</div><div class="l">爆头率</div></div>
</div>

{fi_html}

{llm_html}

<div class="grid">
<div class="card"><h2>全局击杀热力图</h2><img src="data:image/png;base64,{hi}"></div>
<div class="card"><h2>个人位置</h2><img src="data:image/png;base64,{phi}"></div></div>
<div class="grid">
<div class="card"><h2>武器统计</h2><img src="data:image/png;base64,{wi}"></div>
<div class="card"><h2>选手数据</h2><img src="data:image/png;base64,{si}"></div></div>
<div class="grid grid-f">
<div class="card"><h2>击杀距离</h2><img src="data:image/png;base64,{di}"></div></div>

<div class="card">
<h2>完整数据</h2>
<table class="tbl"><thead><tr><th>选手</th><th>阵营</th><th>击杀</th><th>死亡</th><th>K/D</th><th>爆头</th><th>HS%</th></tr></thead>
<tbody>{rows}</tbody></table></div>

<div class="ft">CS2 Agent | 离线解析 + AI 教练点评</div>
</div></body></html>"""

    output_path = Path(output_path)
    output_path.write_text(html, encoding="utf-8")
    return str(output_path)

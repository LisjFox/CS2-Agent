""" 图表生成 — Matplotlib 可视化 """

import base64
from io import BytesIO
from collections import Counter

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.font_manager as fm

from config import C_T, C_CT, C_BG, C_BG2, C_TEXT, C_ACCENT, C_GREEN, C_ORANGE, C_DEATH, C_KILL

# ── 中文字体 Fallback ──
_CN_FONTS = ["Microsoft YaHei", "SimHei", "DengXian", "Noto Sans CJK SC", "WenQuanYi Micro Hei"]
for f in _CN_FONTS:
    try:
        fm.findfont(f, fallback_to_default=False)
        plt.rcParams["font.sans-serif"] = [f] + plt.rcParams["font.sans-serif"]
        plt.rcParams["axes.unicode_minus"] = False
        break
    except Exception:
        continue

plt.rcParams.update({
    "figure.facecolor": C_BG, "axes.facecolor": C_BG2,
    "text.color": C_TEXT, "axes.labelcolor": C_TEXT,
    "axes.edgecolor": "#555", "axes.grid": False,
})


def _b64(fig):
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight",
               facecolor=C_BG, edgecolor="none")
    buf.seek(0)
    plt.close(fig)
    return base64.b64encode(buf.read()).decode()


def _map_img(map_name):
    from pathlib import Path
    from awpy.data import MAPS_DIR
    for c in [f"{map_name}.png", f"{map_name.replace('_lower','')}.png"]:
        p = MAPS_DIR / c
        if p.exists():
            return mpimg.imread(p)
    return None


def _game_to_pixel(map_name, x, y):
    from awpy.plot.utils import game_to_pixel_axis
    return game_to_pixel_axis(map_name, x, "x"), game_to_pixel_axis(map_name, y, "y")


def gen_heatmap(data):
    """击杀热力图."""
    from awpy.plot.utils import game_to_pixel_axis
    fig, ax = plt.subplots(figsize=(10, 10))
    bg = _map_img(data["map_name"])
    if bg is not None:
        ax.imshow(bg, zorder=0)
    ax.axis("off")

    for kp in data["kill_positions"]:
        try:
            px, py = game_to_pixel_axis(data["map_name"], kp["x"], "x"), \
                     game_to_pixel_axis(data["map_name"], kp["y"], "y")
        except Exception:
            continue
        if 0 <= px <= 1024 and 0 <= py <= 1024:
            c = C_CT if kp["victim_team"] == 3 else C_T
            m = "x" if kp["victim_team"] == 3 else "o"
            ax.scatter(px, py, c=c, s=25, alpha=0.35, marker=m, linewidths=0.5)

    ax.set_title(f"{data['map_name']} — 击杀分布 ({len(data['kill_positions'])} kills)",
                 color="white", fontsize=14, pad=10)
    fig.patch.set_facecolor("#111")
    return _b64(fig)


def gen_weapon_chart(data):
    """武器统计图."""
    top = data["weapon_stats"][:12]
    if not top:
        return ""
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 5),
                                  gridspec_kw={"width_ratios": [2, 1]})
    names = [w["weapon"][:15] for w in top]
    kills = [w["kills"] for w in top]
    cp = [C_T, C_CT, C_GREEN, C_ORANGE, C_ACCENT, "#9B59B6", "#1ABC9C",
          "#F39C12", "#3498DB", "#E74C3C", "#2ECC71", "#E67E22"]
    bars = a1.barh(range(len(names)), kills, color=cp[:len(names)],
                   edgecolor="white", linewidth=0.5)
    a1.set_yticks(range(len(names)))
    a1.set_yticklabels(names, fontsize=9)
    a1.set_xlabel("击杀", color="white")
    a1.invert_yaxis()
    a1.set_title("武器击杀 Top 12", color="white", fontsize=13)
    for b, k in zip(bars, kills):
        a1.text(b.get_width() + 0.3, b.get_y() + b.get_height() / 2,
                str(k), va="center", fontsize=9, color="white")
    top5 = [w for w in data["weapon_stats"][:6]]
    if sum(w["kills"] for w in top5) > 0:
        a2.pie([w["kills"] for w in top5],
               labels=[w["weapon"][:10] for w in top5],
               autopct="%1.0f%%", colors=cp, startangle=90,
               textprops={"color": "white", "fontsize": 8})
        a2.set_title("击杀占比", color="white", fontsize=13)
    fig.patch.set_facecolor(C_BG)
    return _b64(fig)


def gen_player_chart(data):
    """选手数据总览."""
    players = sorted(data["player_stats"].values(),
                     key=lambda p: p["kills"], reverse=True)
    names = [p["name"][:12] for p in players]
    kills = [p["kills"] for p in players]
    deaths = [p["deaths"] for p in players]
    hs_pcts = [p["hs_pct"] for p in players]
    kds = [p["kd"] for p in players]

    fig, axes = plt.subplots(2, 2, figsize=(14, 8))
    fig.patch.set_facecolor(C_BG)

    ax = axes[0, 0]
    x = range(len(names))
    ax.bar(x, kills, 0.35, label="击杀", color=C_KILL, alpha=0.8)
    ax.bar([i + 0.35 for i in x], deaths, 0.35, label="死亡", color=C_DEATH, alpha=0.8)
    ax.set_xticks([i + 0.175 for i in x])
    ax.set_xticklabels(names, fontsize=8, rotation=30, ha="right")
    ax.legend(fontsize=8)
    ax.set_title("K/D 对比", color="white", fontsize=12)

    ax = axes[0, 1]
    chs = [C_GREEN if p["hs_pct"] >= 60 else C_ORANGE
           if p["hs_pct"] >= 40 else C_ACCENT for p in players]
    ax.barh(names, hs_pcts, color=chs, edgecolor="white", linewidth=0.5)
    ax.set_xlabel("爆头率 %", color="white")
    ax.set_title("爆头率", color="white", fontsize=12)
    for p, b in zip(players, ax.patches):
        ax.text(b.get_width() + 1, b.get_y() + b.get_height() / 2,
                f"{p['hs_pct']}%", va="center", fontsize=8, color="white")

    ax = axes[1, 0]
    ckd = [C_KILL if k >= 1 else C_DEATH for k in kds]
    bars = ax.bar(names, kds, color=ckd, alpha=0.8)
    ax.set_ylabel("K/D", color="white")
    ax.set_title("K/D Ratio", color="white", fontsize=12)
    ax.tick_params(axis="x", rotation=30, labelsize=8)
    for b, kd in zip(bars, kds):
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.05,
                f"{kd:.2f}", ha="center", fontsize=8, color="white")

    axes[1, 1].axis("off")
    tc = Counter(p["team_name"] for p in players)
    tlines = ["团队配置", ""] + [f"  {t}: {c}" for t, c in tc.items()]
    axes[1, 1].text(0.1, 0.7, "\n".join(tlines), fontsize=11, color="white",
                    va="top", bbox=dict(boxstyle="round", facecolor=C_BG2, edgecolor="#555"))
    plt.tight_layout()
    return _b64(fig)


def gen_distance_chart(data):
    """击杀距离散点图."""
    dists = [kp["distance"] for kp in data["kill_positions"]]
    hs = [kp["headshot"] for kp in data["kill_positions"]]
    if not dists:
        return ""
    fig, ax = plt.subplots(figsize=(10, 4))
    fig.patch.set_facecolor(C_BG)
    colors = [C_GREEN if h else C_ACCENT for h in hs]
    ax.scatter(range(len(dists)), dists, c=colors, s=15, alpha=0.6)
    if len(dists) > 5:
        w = min(10, len(dists) // 3)
        ma = np.convolve(dists, np.ones(w) / w, mode="valid")
        ax.plot(range(w - 1, w - 1 + len(ma)), ma, color="#3498DB", linewidth=1.5, alpha=0.8)
    ax.set_xlabel("击杀顺序", color="white")
    ax.set_ylabel("距离 (米)", color="white")
    ax.set_title("击杀距离 (绿色=爆头)", color="white", fontsize=12)
    ax.axhline(y=np.mean(dists), color=C_T, linestyle="--", alpha=0.5,
               label=f"平均 {np.mean(dists):.1f}m")
    ax.legend(fontsize=8)
    return _b64(fig)


def gen_player_heatmap(data, player_sid):
    """个人击杀/阵亡位置图."""
    kills = [kp for kp in data["kill_positions"] if kp["killer_sid"] == player_sid]
    deaths = [kp for kp in data["kill_positions"] if kp["victim_sid"] == player_sid]
    if not kills and not deaths:
        return ""

    from awpy.plot.utils import game_to_pixel_axis
    fig, ax = plt.subplots(figsize=(8, 8))
    bg = _map_img(data["map_name"])
    if bg is not None:
        ax.imshow(bg, zorder=0)
    ax.axis("off")

    for kp in kills:
        try:
            px, py = game_to_pixel_axis(data["map_name"], kp["x"], "x"), \
                     game_to_pixel_axis(data["map_name"], kp["y"], "y")
        except Exception:
            continue
        if 0 <= px <= 1024 and 0 <= py <= 1024:
            ax.scatter(px, py, c=C_KILL, s=50, alpha=0.6, marker="o",
                      edgecolors="white", linewidth=0.5)
    for kp in deaths:
        try:
            px, py = game_to_pixel_axis(data["map_name"], kp["x"], "x"), \
                     game_to_pixel_axis(data["map_name"], kp["y"], "y")
        except Exception:
            continue
        if 0 <= px <= 1024 and 0 <= py <= 1024:
            ax.scatter(px, py, c=C_DEATH, s=60, alpha=0.7, marker="x",
                      edgecolors="white", linewidth=1.5)

    ax.set_title("个人击杀/阵亡 [绿=击杀 红=阵亡]", color="white", fontsize=12)
    fig.patch.set_facecolor("#111")
    return _b64(fig)

""" Demo 解析 — 读取 .dem 文件，提取击杀/位置/武器/选手数据 """

import warnings
from pathlib import Path
from collections import Counter

warnings.filterwarnings("ignore")
import numpy as np

from config import WEAPON_NAMES, WEAPON_CATS


def clean_weapon(w):
    return WEAPON_NAMES.get(w, w.replace("_", " ").title())


def parse_demo(demo_path):
    """解析 .dem 文件，返回结构化数据字典."""
    from awpy import Demo

    path = Path(demo_path)
    demo = Demo(str(path))
    map_name = demo.header["map_name"]

    deaths = demo.parser.parse_event("player_death")
    hurts = demo.parser.parse_event("player_hurt")
    round_starts = demo.parser.parse_event("round_start")
    player_info = demo.parser.parse_player_info()

    # --- 各回合起始 tick ---
    round_ticks = sorted(round_starts["tick"].unique()) if len(round_starts) > 0 else []

    # -- Kill positions --
    kill_ticks = sorted(deaths["tick"].unique())
    tick_data = demo.parser.parse_ticks(["X", "Y", "team_num"], ticks=kill_ticks)
    pos_lookup = {}
    for _, r in tick_data.iterrows():
        pos_lookup[(int(r["tick"]), str(r["steamid"]))] = (
            float(r["X"]), float(r["Y"]),
            int(r["team_num"]) if r["team_num"] else None
        )

    # --- 给每个击杀分配回合号 ---
    def _round_of_tick(t):
        for i in range(len(round_ticks) - 1, -1, -1):
            if t >= round_ticks[i]:
                return i + 1
        return 1

    kill_positions = []
    for _, death in deaths.iterrows():
        key = (int(death["tick"]), str(death["user_steamid"]))
        if key in pos_lookup:
            x, y, team = pos_lookup[key]
            kr = player_info[player_info["steamid"].astype(str) == str(death["attacker_steamid"])]
            kt = int(kr.iloc[0]["team_number"]) if len(kr) > 0 else None
            kill_positions.append({
                "tick": int(death["tick"]),
                "round": _round_of_tick(int(death["tick"])),
                "killer": death["attacker_name"],
                "killer_sid": str(death["attacker_steamid"]),
                "victim": death["user_name"],
                "victim_sid": str(death["user_steamid"]),
                "weapon": death["weapon"],
                "headshot": bool(death["headshot"]),
                "distance": float(death["distance"]),
                "x": x, "y": y,
                "killer_team": kt, "victim_team": team,
            })

    # -- Player stats --
    player_stats = {}
    for _, info in player_info.iterrows():
        sid = str(info["steamid"])
        team = int(info["team_number"])
        k = deaths[deaths["attacker_steamid"] == sid]
        d = deaths[deaths["user_steamid"] == sid]
        hs = k[k["headshot"] == True]
        player_stats[sid] = {
            "name": info["name"], "steamid": sid,
            "team": team, "team_name": {2: "T", 3: "CT"}.get(team, "?"),
            "kills": len(k), "deaths": len(d), "hs": len(hs),
            "hs_pct": round(len(hs) / len(k) * 100, 1) if len(k) > 0 else 0,
            "kd": round(len(k) / max(len(d), 1), 2),
        }

    # -- Weapon stats --
    wc, whs = Counter(), Counter()
    for _, death in deaths.iterrows():
        wc[death["weapon"]] += 1
        if death["headshot"]:
            whs[death["weapon"]] += 1
    weapon_stats = []
    for w, c in wc.most_common():
        weapon_stats.append({
            "weapon": clean_weapon(w), "weapon_raw": w,
            "kills": c, "hs": whs.get(w, 0),
            "hs_pct": round(whs.get(w, 0) / c * 100, 1),
        })

    # --- 按回合组织数据 ---
    round_data = {}
    for i in range(len(round_ticks)):
        r = i + 1
        round_kills = [kp for kp in kill_positions if kp["round"] == r]
        round_data[r] = {
            "round": r,
            "kills": len(round_kills),
            "kill_seq": [{
                "killer": kp["killer"],
                "victim": kp["victim"],
                "weapon": clean_weapon(kp["weapon"]),
                "headshot": kp["headshot"],
            } for kp in round_kills],
        }

    return {
        "demo": demo, "map_name": map_name,
        "deaths": deaths, "hurts": hurts,
        "kill_positions": kill_positions,
        "player_stats": player_stats,
        "weapon_stats": weapon_stats,
        "total_kills": len(deaths),
        "total_rounds": len(round_starts),
        "total_players": len(player_info),
        "round_data": round_data,
    }

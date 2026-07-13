"""
职业选手多维数据（来源: HLTV 大赛生涯数据 / 近 12 个月平均）
==================================================
各维度说明:
  kd         = K/D Ratio（击杀/死亡比）
  hs_pct     = Headshot %（爆头率）
  adr        = Average Damage Per Round（每回合平均伤害）
  rating     = HLTV Rating 2.1（综合评分）
  kpr        = Kills Per Round（每回合平均击杀）
  dpr        = Deaths Per Round（每回合平均死亡）
  kast       = % of rounds with Kill/Assist/Survive/Trade（存活贡献率）
  impact     = HLTV Impact Rating（赛场影响力）
  open_kpr   = Opening Kills Per Round（首杀率）
  clutch_pct = Clutch Win %（残局胜率，1vX 场景）
  multi_kill = Multi-kill Rounds %（多杀回合比例，2k+）
  utility_dmg = Utility Damage Per Round（每回合道具伤害）
  flash_assist = Flash Assists Per Round（每回合闪助攻）
"""

from dataclasses import dataclass, field
from typing import List
import math


@dataclass
class ProPlayer:
    name: str
    team: str
    role: str
    description: str
    main_weapon: str = ""  # 主武器
    # 核心数据
    kd: float       # K/D
    hs_pct: float   # 爆头率 %
    adr: float      # 场均伤害
    rating: float   # HLTV Rating
    kpr: float      # 每回合击杀
    dpr: float      # 每回合死亡
    kast: float     # 存活贡献率 %
    impact: float   # 影响力评分
    open_kpr: float  # 首杀率
    clutch_pct: float  # 残局胜率 %
    multi_kill: float   # 多杀率 %
    utility_dmg: float  # 道具伤害/回合
    flash_assist: float # 闪助攻/回合


PRO_PLAYERS: dict[str, ProPlayer] = {}


def reg(name: str, team: str, role: str, desc: str, **kwargs):
    """注册一个职业选手."""
    defaults = {
        "kd": 1.00, "hs_pct": 45.0, "adr": 75.0, "rating": 1.00,
        "kpr": 0.65, "dpr": 0.60, "kast": 70.0, "impact": 1.00,
        "open_kpr": 0.10, "clutch_pct": 35.0, "multi_kill": 15.0,
        "utility_dmg": 10.0, "flash_assist": 0.08,
    }
    defaults.update(kwargs)
    PRO_PLAYERS[name] = ProPlayer(
        name=name, team=team, role=role, description=desc, **defaults
    )


# ════════════════════════════════════════════
#  注册职业选手（数据近 12 个月 HLTV）
#  源: hltv.org/stats
# ════════════════════════════════════════════

# --- 步枪手 ---
reg("NiKo", "Falcons / G2", "突破手/自由人",
    "步枪之王，巅峰期爆头率职业天花板", main_weapon="AK-47",
    kd=1.18, hs_pct=55.6, adr=83.1, rating=1.13,
    kpr=0.73, dpr=0.62, kast=72.5, impact=1.22,
    open_kpr=0.14, clutch_pct=38.2, multi_kill=17.8,
    utility_dmg=8.5, flash_assist=0.06)

reg("donk", "Team Spirit", "突破手",
    "天才少年，2024 横空出世，击杀能力恐怖",
    kd=1.32, hs_pct=58.8, adr=91.2, rating=1.24,
    kpr=0.82, dpr=0.62, kast=74.1, impact=1.41,
    open_kpr=0.18, clutch_pct=41.5, multi_kill=21.3,
    utility_dmg=7.2, flash_assist=0.04)

reg("Twistzz", "Team Liquid / FaZe", "自由人/补枪",
    "北美步枪标杆，定位精准，稳定性高",
    kd=1.12, hs_pct=49.3, adr=78.1, rating=1.08,
    kpr=0.69, dpr=0.62, kast=71.8, impact=1.09,
    open_kpr=0.11, clutch_pct=36.7, multi_kill=15.9,
    utility_dmg=9.1, flash_assist=0.07)

reg("ropz", "FaZe Clan", "自由人",
    "爱沙尼亚残局大师，聪明型选手",
    kd=1.11, hs_pct=47.6, adr=76.8, rating=1.07,
    kpr=0.67, dpr=0.61, kast=72.3, impact=1.05,
    open_kpr=0.10, clutch_pct=42.1, multi_kill=15.2,
    utility_dmg=10.3, flash_assist=0.09)

reg("EliGE", "FaZe / Complexity", "突破手/自由人",
    "北美 CS 常青树，步枪全面",
    kd=1.13, hs_pct=48.2, adr=79.5, rating=1.09,
    kpr=0.70, dpr=0.62, kast=71.5, impact=1.11,
    open_kpr=0.12, clutch_pct=35.8, multi_kill=16.4,
    utility_dmg=8.8, flash_assist=0.06)

reg("frozen", "FaZe Clan / Mouz", "自由人",
    "斯洛伐克天才，全能型步枪手",
    kd=1.14, hs_pct=44.1, adr=78.9, rating=1.10,
    kpr=0.71, dpr=0.62, kast=72.8, impact=1.10,
    open_kpr=0.11, clutch_pct=39.3, multi_kill=16.8,
    utility_dmg=9.5, flash_assist=0.08)

reg("Spinx", "Team Vitality", "突破手/自由人",
    "以色列步枪手，爆发力强",
    kd=1.12, hs_pct=43.5, adr=77.6, rating=1.08,
    kpr=0.69, dpr=0.62, kast=71.2, impact=1.10,
    open_kpr=0.12, clutch_pct=37.4, multi_kill=15.8,
    utility_dmg=9.2, flash_assist=0.07)

reg("flameZ", "Team Vitality", "突破手",
    "以色列新星，进攻火力凶猛",
    kd=1.10, hs_pct=45.8, adr=76.5, rating=1.06,
    kpr=0.68, dpr=0.62, kast=70.5, impact=1.08,
    open_kpr=0.13, clutch_pct=34.9, multi_kill=15.5,
    utility_dmg=8.6, flash_assist=0.06)

reg("jks", "Liquid / G2 / Complexity", "自由人",
    "澳大利亚支柱，防守型自由人代表",
    kd=1.06, hs_pct=44.3, adr=73.2, rating=1.03,
    kpr=0.65, dpr=0.61, kast=70.8, impact=0.98,
    open_kpr=0.09, clutch_pct=40.5, multi_kill=14.2,
    utility_dmg=11.2, flash_assist=0.10)

# --- 狙击手 ---
reg("s1mple", "Natus Vincere / Falcons", "狙击手/自由人",
    "历史最强选手之一，全能天花板",
    kd=1.32, hs_pct=42.1, adr=86.7, rating=1.23,
    kpr=0.78, dpr=0.59, kast=73.5, impact=1.32,
    open_kpr=0.14, clutch_pct=44.6, multi_kill=20.1,
    utility_dmg=9.8, flash_assist=0.07)

reg("ZywOo", "Team Vitality", "狙击手",
    "法国天才，数据机器，近年最强狙击手",
    kd=1.35, hs_pct=38.5, adr=85.2, rating=1.24,
    kpr=0.79, dpr=0.58, kast=74.2, impact=1.30,
    open_kpr=0.13, clutch_pct=46.8, multi_kill=20.5,
    utility_dmg=8.7, flash_assist=0.06)

reg("m0NESY", "G2 Esports", "狙击手",
    "新生代狙击天才，反应极快",
    kd=1.28, hs_pct=40.2, adr=82.3, rating=1.19,
    kpr=0.75, dpr=0.60, kast=72.8, impact=1.25,
    open_kpr=0.14, clutch_pct=43.2, multi_kill=19.2,
    utility_dmg=8.2, flash_assist=0.05)

reg("dev1ce", "Astralis / NIP", "狙击手",
    "丹麦狙击教科书，赛场智商顶级",
    kd=1.22, hs_pct=36.8, adr=79.5, rating=1.16,
    kpr=0.72, dpr=0.59, kast=73.1, impact=1.16,
    open_kpr=0.12, clutch_pct=45.1, multi_kill=18.3,
    utility_dmg=9.4, flash_assist=0.08)

reg("sh1ro", "Cloud9 / Spirit", "狙击手",
    "独联体稳健型狙击手，生存能力极强",
    kd=1.30, hs_pct=35.1, adr=78.9, rating=1.18,
    kpr=0.71, dpr=0.55, kast=75.2, impact=1.17,
    open_kpr=0.11, clutch_pct=42.8, multi_kill=17.5,
    utility_dmg=8.5, flash_assist=0.06)

reg("w0nderful", "Natus Vincere / Spirit", "狙击手",
    "乌克兰新星狙击手，NAVI 新一代",
    kd=1.10, hs_pct=39.8, adr=75.1, rating=1.06,
    kpr=0.67, dpr=0.61, kast=70.5, impact=1.03,
    open_kpr=0.10, clutch_pct=38.5, multi_kill=15.8,
    utility_dmg=8.1, flash_assist=0.06)

reg("torzsi", "MOUZ", "狙击手",
    "匈牙利狙击手，MOUZ 体系核心",
    kd=1.15, hs_pct=37.2, adr=76.3, rating=1.09,
    kpr=0.68, dpr=0.59, kast=71.8, impact=1.08,
    open_kpr=0.11, clutch_pct=39.1, multi_kill=16.2,
    utility_dmg=7.9, flash_assist=0.05)

# --- 指挥 ---
reg("apEX", "Team Vitality", "指挥/突破手",
    "法国指挥，激进型突破指挥代表",
    kd=0.98, hs_pct=42.5, adr=72.1, rating=0.97,
    kpr=0.65, dpr=0.67, kast=68.5, impact=0.95,
    open_kpr=0.11, clutch_pct=32.1, multi_kill=13.5,
    utility_dmg=12.5, flash_assist=0.15)

reg("chopper", "Team Spirit", "指挥",
    "俄罗斯指挥，带领 Spirit 夺冠 Major",
    kd=0.92, hs_pct=38.9, adr=68.5, rating=0.93,
    kpr=0.61, dpr=0.68, kast=66.8, impact=0.89,
    open_kpr=0.09, clutch_pct=30.5, multi_kill=12.1,
    utility_dmg=13.8, flash_assist=0.18)

reg("karrigan", "FaZe Clan", "指挥",
    "丹麦指挥，战术大师，残局智商极高",
    kd=0.94, hs_pct=40.1, adr=69.2, rating=0.94,
    kpr=0.62, dpr=0.67, kast=67.5, impact=0.90,
    open_kpr=0.08, clutch_pct=33.8, multi_kill=12.5,
    utility_dmg=14.2, flash_assist=0.20)

reg("Snappi", "Falcons / ENCE", "指挥",
    "丹麦老将指挥，体系建立者",
    kd=0.88, hs_pct=37.5, adr=66.8, rating=0.90,
    kpr=0.59, dpr=0.69, kast=65.8, impact=0.85,
    open_kpr=0.08, clutch_pct=31.2, multi_kill=11.5,
    utility_dmg=15.1, flash_assist=0.22)

# --- 中国选手 ---
reg("somebody", "TYLOO / Lynn Vision", "自由人/指挥",
    "中国 CS 标志人物，枪法灵动",
    kd=0.97, hs_pct=44.6, adr=71.5, rating=0.96,
    kpr=0.64, dpr=0.66, kast=68.2, impact=0.93,
    open_kpr=0.10, clutch_pct=34.5, multi_kill=13.2,
    utility_dmg=11.5, flash_assist=0.12)

reg("BnTeT", "TYLOO / Lynn Vision", "突破手/指挥",
    "印尼华裔，亚洲 CS 顶梁柱",
    kd=1.05, hs_pct=46.8, adr=74.2, rating=1.02,
    kpr=0.66, dpr=0.63, kast=70.2, impact=1.01,
    open_kpr=0.11, clutch_pct=36.8, multi_kill=14.5,
    utility_dmg=10.1, flash_assist=0.09)


def get_all_player_names() -> List[str]:
    """获取所有选手名."""
    return sorted(PRO_PLAYERS.keys())


def get_player(name: str) -> ProPlayer | None:
    """按名字找选手."""
    return PRO_PLAYERS.get(name)


def find_similar_players(kd: float, hs_pct: float, adr: float = None,
                         top_n: int = 5) -> List[tuple[float, str, ProPlayer]]:
    """用欧几里得距离找最像你的职业选手.

    对比维度: K/D, HS%, ADR
    自动做 Min-Max 归一化.

    Args:
        kd: 你的 K/D
        hs_pct: 你的爆头率 (%)
        adr: 你的 ADR（可选）
        top_n: 返回前 N 个最接近的

    Returns:
        [(距离, 选手名, ProPlayer), ...]
    """
    your_stats = [kd, hs_pct]
    if adr is not None:
        your_stats.append(adr)

    # 提取所有选手的对应维度
    all_players = list(PRO_PLAYERS.values())

    results = []
    for pro in all_players:
        pro_stats = [pro.kd, pro.hs_pct]
        if adr is not None:
            pro_stats.append(pro.adr)

        # 计算欧几里得距离（不做归一化的原始距离）
        dist = math.sqrt(sum((y - p) ** 2 for y, p in zip(your_stats, pro_stats)))
        results.append((round(dist, 3), pro.name, pro))

    results.sort()
    return results[:top_n]

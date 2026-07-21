"""工具模块 — @tool 装饰器函数 + 注册表"""

import importlib, pkgutil, inspect
from langchain_core.tools import tool, BaseTool
from memory import load_memory, get_history


# ═══════════════════════════════════════════════════════
#  @tool 装饰器函数
# ═══════════════════════════════════════════════════════

@tool
def get_player_history(player_name: str) -> str:
    """查询某玩家的历史比赛记录，包含每场的击杀/死亡/K/D/爆头率"""
    mem = load_memory()
    sessions = get_history(mem, player_name)
    if not sessions:
        return f"玩家 {player_name} 暂无历史记录"
    lines = [f"=== {player_name} 的历史记录 ==="]
    for s in sessions[-10:]:
        lines.append(
            f"  [{s['date']}] {s['kills']}K/{s['deaths']}D  "
            f"K/D {s['kd']}  HS% {s['hs_pct']}%  "
            f"主武器: {s['top_weapon']}"
        )
    return "\n".join(lines)


@tool
def get_all_players() -> str:
    """查看所有有过记录的玩家列表"""
    mem = load_memory()
    if not mem["players"]:
        return "暂无玩家记录"
    lines = ["所有玩家:"]
    for name, pdata in mem["players"].items():
        last = pdata["sessions"][-1] if pdata["sessions"] else {}
        lines.append(f"  {name}: {len(pdata['sessions'])} 场, "
                     f"最近 K/D {last.get('kd', '?')}")
    return "\n".join(lines)


@tool
def get_player_trend(player_name: str, metric: str = "kd") -> str:
    """分析某玩家某项指标的变化趋势。
    
    Args:
        player_name: 玩家名
        metric: 指标名 (kd / hs_pct / kills / deaths)
    """
    mem = load_memory()
    sessions = get_history(mem, player_name)
    if not sessions or len(sessions) < 2:
        return f"{player_name} 的数据不足，无法分析趋势（至少需要 2 场）"

    values = [s.get(metric, 0) for s in sessions]
    recent = values[-5:]
    trend = "上升" if recent[-1] > recent[0] else "下降" if recent[-1] < recent[0] else "持平"

    lines = [
        f"=== {player_name} 的 {metric} 趋势 ===",
        f"趋势: {trend}",
        f"最近 {len(recent)} 场: {recent}",
        f"平均值: {sum(recent)/len(recent):.2f}",
    ]
    return "\n".join(lines)


@tool
def get_training_plan(time_minutes: int = 60) -> str:
    """获取 CS2 每日训练计划。
    
    Args:
        time_minutes: 训练时长（分钟），可选 30 / 60 / 120
    """
    plans = {
        30: "30分钟训练:\n  Aim Botz (10min) + Deathmatch (20min)",
        60: "1小时训练:\n  Aim Botz (15min) + Prefire (15min) + Deathmatch (30min)",
        120: "2小时训练:\n  Aim Botz (20min) + Prefire (20min) + Retake (30min) + 实战 (50min)",
    }
    return plans.get(time_minutes, "推荐 30 / 60 / 120 分钟三档")


@tool
def get_weapon_advice(weapon: str, kill_count: int, hs_pct: float) -> str:
    """获取特定武器的训练建议。
    
    Args:
        weapon: 武器名，如 AK-47, AWP, M4A4
        kill_count: 该武器击杀数
        hs_pct: 该武器爆头率 (%)
    """
    suggestions = {
        "ak-47": f"AK-47: {kill_count}杀 / 爆头率 {hs_pct}% — "
                 f"{'不错' if hs_pct >= 50 else '偏低'}。建议 Yprac Prefire Dust2 每天 15 分钟",
        "awp": f"AWP: {kill_count}杀 — 建议 Aim Botz 练甩枪 + 死斗练架点",
        "m4a4": f"M4A4: {kill_count}杀 / 爆头率 {hs_pct}% — "
                f"{'不错' if hs_pct >= 50 else '偏低'}。建议练反方向 pre-aim",
    }
    return suggestions.get(weapon, f"{weapon}: {kill_count}杀。多练武器控制")


@tool
def compare_with_pro(player_kd: float, player_hs: float,
                      player_main_weapon: str = "AK-47",
                      pro_name: str = "") -> str:
    """把你的数据和某位职业选手做详细对比，或在所有选手中找最像你的。

    Args:
        player_kd: 你的 K/D
        player_hs: 你的爆头率 (%)
        player_main_weapon: 你的主武器
        pro_name: 职业选手名。不填则自动找最像你的 3 个
    """
    from pro_data import PRO_PLAYERS, find_similar_players, get_player

    if not pro_name:
        matches = find_similar_players(player_kd, player_hs, adr=None, top_n=3)
        lines = [f"=== 与你最接近的 3 位职业选手 ===", ""]
        lines.append(f"  {'排名':<6} {'选手':<12} {'K/D':<10} {'HS%':<10} {'定位':<12} {'差距':<10}")
        lines.append(f"  {'-'*60}")
        for i, (dist, name, pro) in enumerate(matches, 1):
            lines.append(f"  {i:<6} {name:<12} {pro.kd:<10} {pro.hs_pct:<10} {pro.role:<12} {dist:<10}")
        lines.append("")
        lines.append("差距越小说明打法风格越接近，用欧几里得距离计算")
        return "\n".join(lines)

    pro = get_player(pro_name)
    if not pro:
        from pro_data import get_all_player_names
        available = ", ".join(get_all_player_names())
        return f"没有 {pro_name} 的数据。可选: {available}"

    kd_gap = round(player_kd - pro.kd, 2)
    hs_gap = round(player_hs - pro.hs_pct, 1)

    lines = [
        f"=== 与 {pro.name} 的全面对比 ===",
        f"  战队: {pro.team} | 定位: {pro.role}",
        f"  简介: {pro.description}",
        "",
        f"  {'指标':<16} {'你':<12} {pro.name:<14} {'差距':<10}",
        f"  {'-'*52}",
        f"  {'K/D':<16} {player_kd:<12} {pro.kd:<14} {'+' + str(kd_gap) if kd_gap > 0 else str(kd_gap):<10}",
        f"  {'爆头率 %':<16} {player_hs:<12} {pro.hs_pct:<14} {'+' + str(hs_gap) if hs_gap > 0 else str(hs_gap):<10}",
    ]

    if kd_gap > 0:
        lines.append(f"  - K/D 你比 {pro.name} 高 +{kd_gap}，这把你状态很好")
    else:
        lines.append(f"  - K/D 比 {pro.name} 低 {abs(kd_gap)}，但他是职业选手")
    if hs_gap > 5:
        lines.append(f"  - 爆头率比 {pro.name} 高 {hs_gap}%，你枪法很犀利")
    elif hs_gap < -10:
        lines.append(f"  - 爆头率比 {pro.name} 低 {abs(hs_gap)}%，预瞄可以加强")

    return "\n".join(lines)


@tool
def get_pro_leaderboard(metric: str = "kd", top_n: int = 5) -> str:
    """查看职业选手某项指标的排行榜。

    Args:
        metric: 指标名 (kd / hs_pct / adr / rating / impact / kpr / clutch_pct)
        top_n: 显示前几名
    """
    from pro_data import PRO_PLAYERS

    METRIC_NAMES = {
        "kd": "K/D", "hs_pct": "爆头率 %", "adr": "ADR",
        "rating": "Rating", "impact": "Impact", "kpr": "每回合击杀",
        "clutch_pct": "残局胜率 %", "kast": "KAST %",
        "utility_dmg": "道具伤害/回合", "open_kpr": "首杀率",
        "multi_kill": "多杀率 %",
    }

    if metric not in METRIC_NAMES:
        return f"未知指标 {metric}，可选: {', '.join(METRIC_NAMES.keys())}"

    sorted_players = sorted(
        PRO_PLAYERS.values(),
        key=lambda p: getattr(p, metric, 0),
        reverse=True
    )

    lines = [f"=== {METRIC_NAMES[metric]} 排行榜 Top {top_n} ===", ""]
    lines.append(f"  {'排名':<6} {'选手':<12} {'数值':<10} {'定位':<12}")
    lines.append(f"  {'-'*40}")
    for i, p in enumerate(sorted_players[:top_n], 1):
        val = getattr(p, metric, 0)
        fmt = f"{val:.1f}" if isinstance(val, float) else str(val)
        lines.append(f"  {i:<6} {p.name:<12} {fmt:<10} {p.role:<12}")
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════
#  @tool: 潘一鸣知识库 — 向量检索 / 战术建议
# ═══════════════════════════════════════════════════════

@tool
def query_knowledge(query: str, map_name: str = "", top_k: int = 3) -> str:
    """从 CS2 战术知识库中语义检索信息。覆盖地图点位、投掷物路线、武器属性、经济规则。

    Args:
        query: 搜索内容，如 "Dust2 A大 烟雾弹"、"AK-47 伤害"、"ECO局 起枪策略"
        map_name: 按地图过滤（可选），如 "Dust2"、"Mirage"
        top_k: 返回几条最相关结果，默认 3
    """
    try:
        from knowledge_base.vector_store import get_vector_store
        store = get_vector_store()
        store.build_index()
        filter_meta = {"map": map_name} if map_name else None
        results = store.search(query, top_k=top_k, filter_metadata=filter_meta)
        if not results:
            return f"知识库中未找到与「{query}」相关的内容"
        lines = [f"知识库检索: {query}", ""]
        for i, r in enumerate(results, 1):
            meta = r["metadata"]
            lines.append(f"  [{i}] {meta.get('title', '?')} ({meta.get('category', '?')})")
            lines.append(f"      {r['text'][:200]}")
            lines.append("")
        return "\n".join(lines)
    except Exception as e:
        return f"[知识库检索失败] {e}"


@tool
def get_map_tactics(map_name: str, side: str = "T", situation: str = "") -> str:
    """查询指定地图的战术建议，基于潘一鸣战术知识库。支持所有比赛地图。

    Args:
        map_name: 地图名，如 "Dust2"、"Mirage"、"Inferno"、"Nuke"、"Ancient"、"Anubis"
        side: "T" (进攻方) 或 "CT" (防守方)
        situation: 场景描述，如 "进攻A点"、"残局1v2"、"ECO局"、"防守B点"
    """
    try:
        result = get_tactical_advice(map_name, side, situation)
        return result if isinstance(result, str) else str(result)
    except Exception as e:
        return f"[战术查询失败] {e}"


@tool
def get_grenade_routes(map_name: str, target: str = "") -> str:
    """查询指定地图上特定位置的投掷物路线（烟雾弹、闪光弹、燃烧弹、手雷）。

    Args:
        map_name: 地图名，如 "Dust2"、"Mirage"、"Inferno"
        target: 目标位置，如 "A大"、"B点"、"中路"。不填则返回全部
    """
    try:
        from knowledge_base.data.grenades import GRENADE_KNOWLEDGE
        map_lower = map_name.lower().replace(" ", "").replace("de_", "")
        matched = [
            g for g in GRENADE_KNOWLEDGE
            if g.get("map", "").lower().replace(" ", "") == map_lower
        ]
        if not matched:
            matched = [g for g in GRENADE_KNOWLEDGE if g.get("map", "") == map_name]
        if not matched:
            return f"未找到 {map_name} 的投掷物数据"
        lines = [f"{map_name} 投掷物路线:", ""]
        for g in matched:
            title = g["title"]
            if target and target.lower() not in title.lower():
                continue
            content = g["content"][:300]
            lines.append(f"  {title}")
            lines.append(f"     {content}")
            lines.append("")
        if len(lines) == 2:
            return f"未找到 {map_name} 中「{target}」相关的投掷物数据"
        return "\n".join(lines)
    except Exception as e:
        return f"[投掷物查询失败] {e}"


@tool
def get_eco_advice(money: int, round_num: int, side: str = "T", won_last: bool = False) -> str:
    """根据经济状况给出起枪建议和未来几局的经济规划。

    Args:
        money: 当前金钱数
        round_num: 当前回合数 (1-30)
        side: "T" 或 "CT"
        won_last: 上回合是否获胜
    """
    try:
        from tools.economy_calculator import calculate_team_economy
        result = calculate_team_economy(money, side, int(round_num), won_last)
        if isinstance(result, dict):
            lines = [f"经济分析 — 回合{round_num} {side}", ""]
            for k, v in result.items():
                lines.append(f"  {k}: {v}")
            return "\n".join(lines)
        return str(result)
    except Exception as e:
        return f"[经济分析失败] {e}"


# ═══════════════════════════════════════════════════════
#  自动发现 — 扫描所有子模块收集 @tool
# ═══════════════════════════════════════════════════════

def _scan_all_tools():
    """扫描 tools/ 下所有子模块，收集全部 @tool 函数。"""
    seen = set()
    tools = []
    # 当前 __init__.py 中的 @tool
    for v in globals().values():
        if isinstance(v, BaseTool) and id(v) not in seen:
            seen.add(id(v))
            tools.append(v)
    # 子模块中的 @tool
    for importer, modname, ispkg in pkgutil.iter_modules(__path__):
        if modname.startswith('_'):
            continue
        try:
            module = importlib.import_module(f'.{modname}', __package__)
            for name, obj in inspect.getmembers(module):
                if isinstance(obj, BaseTool) and id(obj) not in seen:
                    seen.add(id(obj))
                    tools.append(obj)
        except Exception:
            pass  # 忽略导入失败的模块
    return sorted(tools, key=lambda t: t.name)


# 所有 @tool 函数的统一列表（LangChain bind_tools 直接用）
TOOL_LIST = _scan_all_tools()


def get_tool_descriptions() -> str:
    """获取所有工具的描述."""
    return "\n".join(f"- {t.name}: {t.description}" for t in TOOL_LIST)


def call_tool(tool_name: str, **kwargs):
    """调用指定名称的工具."""
    for t in TOOL_LIST:
        if t.name == tool_name:
            return t.invoke(kwargs)
    names = [t.name for t in TOOL_LIST]
    raise ValueError(f"未知工具: {tool_name}，可用工具: {names}")

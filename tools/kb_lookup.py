"""知识库原生数据查询 — 快速查地图/道具/武器/经济 @tool"""

from langchain_core.tools import tool


@tool
def lookup_knowledge(topic: str, query: str = "") -> str:
    """快速查询 CS2 知识库原生数据，比向量检索更快更直接。适合查具体数值和定义。

    Args:
        topic: 查询类别 — weapon / map / grenade / economy / builds
        query: 关键词，精准匹配类别下的条目，为空则返回概览
    """
    topic = topic.lower().strip()
    q = query.lower().strip()

    if topic == "weapon":
        return _query_weapons(q)
    elif topic == "map":
        return _query_maps(q)
    elif topic == "grenade":
        return _query_grenades(q)
    elif topic == "economy":
        return _query_economy(q)
    elif topic == "builds":
        return _query_builds(q)
    else:
        return "topic 可选: weapon / map / grenade / economy / builds"


def _query_weapons(q: str) -> str:
    from knowledge_base.data.weapons import WEAPON_CATEGORIES, WEAPON_BUILDS

    lines = []
    if not q:
        for cat, weapons in WEAPON_CATEGORIES.items():
            lines.append(f"【{cat}】{', '.join(weapons)}")
        lines.append("")
        lines.append("用 topic=weapon, query=武器名 查看详情。")
        lines.append("用 topic=builds 查看推荐配装。")
        return "\n".join(lines)

    # 按分类搜索
    for cat, weapons in WEAPON_CATEGORIES.items():
        for w in weapons:
            if q in w.lower():
                lines.append(f"  {w} — {cat}")

    if lines:
        lines.insert(0, f"搜索结果（{q}）:")
        return "\n".join(lines)

    return f"未找到武器「{query}」。可用分类: {', '.join(WEAPON_CATEGORIES.keys())}"


def _query_maps(q: str) -> str:
    from knowledge_base.data.maps import MAP_KNOWLEDGE, AVAILABLE_MAPS

    if not q:
        return f"可用地图: {', '.join(AVAILABLE_MAPS)}\n\n用 topic=map, query=地图名 查看详情。"

    results = []
    for m in MAP_KNOWLEDGE:
        map_name = m.get("map", "")
        title = m.get("title", "")
        content = m.get("content", "")
        if q in map_name.lower() or q in title.lower():
            results.append(f"[{map_name}] {title}\n{content[:300]}")

    if results:
        return "\n\n---\n\n".join(results[:5])
    return f"未找到地图「{query}」。可用: {', '.join(AVAILABLE_MAPS)}"


def _query_grenades(q: str) -> str:
    from knowledge_base.data.grenades import GRENADE_KNOWLEDGE

    if not q:
        return "投掷物知识库（33 条记录），包含烟雾弹、闪光弹、燃烧弹、高爆手雷的机制与战术。\n用 topic=grenade, query=关键词 搜索。\n例: query=Mirage 查该地图投掷物路线"

    results = []
    for g in GRENADE_KNOWLEDGE:
        title = g.get("title", "")
        content = g.get("content", "")
        map_name = g.get("map", "")
        if q in title.lower() or q in content.lower() or q in map_name.lower():
            prefix = f"[{map_name}] " if map_name else ""
            results.append(f"{prefix}{title}\n{content[:300]}")

    if results:
        return "\n\n---\n\n".join(results[:5])
    return f"未找到匹配的投掷物记录（query={query}）。"


def _query_economy(q: str) -> str:
    from knowledge_base.data.economy import ECONOMY_CONSTANTS

    if not q:
        import json
        keys = list(ECONOMY_CONSTANTS.keys())
        # 只显示 key 列表，不暴露数值细节
        return f"经济常量: {', '.join(keys)}\n\n用 topic=economy, query=loss_bonus（或其他常量名）查看具体数值。"

    q_clean = q.replace(" ", "_").lower()
    for key in ECONOMY_CONSTANTS:
        if q_clean in key.lower():
            val = ECONOMY_CONSTANTS[key]
            return f"{key}: {val}"

    return f"未找到经济常量「{query}」。可用: {', '.join(ECONOMY_CONSTANTS.keys())}"


def _query_builds(q: str) -> str:
    from knowledge_base.data.weapons import WEAPON_BUILDS

    if not q:
        return f"推荐配装:\n" + "\n".join(f"  {k}" for k in WEAPON_BUILDS.keys()) + \
               "\n\n用 topic=builds, query=配装名 查看推荐购买方案。"

    for key, val in WEAPON_BUILDS.items():
        if q in key.lower():
            return f"【{key}】\n{val}"

    return f"未找到配装「{query}」。可用: {', '.join(WEAPON_BUILDS.keys())}"

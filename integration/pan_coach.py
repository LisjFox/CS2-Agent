"""
潘一鸣的战术教练 — 完整实现
=============================
基于知识库 + LLM 的 CS2 战术分析引擎。
"""

import sys
from pathlib import Path
from collections import defaultdict

# ── 路径导入 ──
# 对方项目路径（demo 解析）
DEMO_PROJECT = str(Path(__file__).parent.parent)
for p in [DEMO_PROJECT]:
    if p not in sys.path:
        sys.path.insert(0, p)

from integration import TacticalCoach, IntegratedCoach


# ── 导入我的知识库模块 ──
try:
    from knowledge_base.data_loader import get_all_knowledge
    from knowledge_base.vector_store import get_vector_store
    from tools.economy_calculator import calculate_team_economy
    from tools.weapon_comparer import WEAPON_STATS
    from tools.map_analyzer import analyze_map
    KB_READY = True
except ImportError as e:
    KB_READY = False
    print(f"[潘一鸣] 知识库导入警告: {e}")

# ── 导入 LLM ──
try:
    from llm import call_llm
    LLM_READY = True
except ImportError:
    try:
        from agent.agent_workflow import CS2Agent
        AGENT_READY = True
    except ImportError:
        AGENT_READY = False
    LLM_READY = False


# ═══════════════════════════════════════════════════
#  地图名映射（demo 格式 → 知识库格式）
# ═══════════════════════════════════════════════════

MAP_NAME_MAP = {
    "de_dust2": "Dust2", "dust2": "Dust2",
    "de_mirage": "Mirage", "mirage": "Mirage",
    "de_inferno": "Inferno", "inferno": "Inferno",
    "de_nuke": "Nuke", "nuke": "Nuke",
    "de_ancient": "Ancient", "ancient": "Ancient",
    "de_anubis": "Anubis", "anubis": "Anubis",
    "de_overpass": "Overpass", "overpass": "Overpass",
    "de_vertigo": "Vertigo", "vertigo": "Vertigo",
}


def normalize_map(map_name: str) -> str:
    """统一地图名格式"""
    return MAP_NAME_MAP.get(map_name.lower(), map_name)


def coord_to_area(map_name: str, x: float, y: float) -> str:
    """坐标 → 区域名称（粗粒度映射，后续可细化）"""
    # 粗略区域判断，精确映射需要地图坐标数据
    if map_name == "Dust2":
        if -2000 < x < -500 and -1000 < y < 500:
            return "匪家/匪洞"
        elif 500 < x < 2000 and -1000 < y < 500:
            return "A大道"
        elif -500 < x < 500 and -500 < y < 500:
            return "中路"
        elif -500 < x < 500 and 500 < y < 1500:
            return "B洞/B包点"
        return "未知区域"
    elif map_name == "Mirage":
        if -2000 < x < -500 and -500 < y < 1000:
            return "A斜坡/A二楼"
        elif -500 < x < 500 and -500 < y < 500:
            return "中路"
        elif -500 < x < 500 and 500 < y < 1500:
            return "B公寓/B包点"
        return "未知区域"
    return "未知区域"


# ═══════════════════════════════════════════════════
#  MyTacticalCoach — 你的完整实现
# ═══════════════════════════════════════════════════

class MyTacticalCoach(TacticalCoach):
    """
    潘一鸣的战术教练。
    用知识库 + LLM 做战术分析，接收 demo 数据，输出战术指导。
    """

    def __init__(self):
        super().__init__()
        self.ready = False

        # 初始化向量知识库
        if KB_READY:
            try:
                self.vector_store = get_vector_store()
                self.knowledge = get_all_knowledge()
                self.ready = True
                print("[潘一鸣] 知识库就绪")
            except Exception as e:
                print(f"[潘一鸣] 知识库初始化失败: {e}")

        # 初始化 LLM 代理
        self.agent = None
        if not LLM_READY:
            try:
                from agent.agent_workflow import CS2Agent
                self.agent = CS2Agent()
                LLM_GLOBAL = True
                print("[潘一鸣] Agent 就绪")
            except Exception as e:
                print(f"[潘一鸣] Agent 初始化失败: {e}")

    # ────────────────────────────────────────────────
    #  方法1: 找值得分析的回合
    # ────────────────────────────────────────────────

    def find_clutch_rounds(self, demo_analysis: dict) -> list[int]:
        """
        从全场数据中找出值得分析的回合。

        判断依据:
        - 残局回合（1v1, 1v2, 1v3）
        - 玩家发挥出色的回合（多杀）
        - 经济翻盘回合
        - 炸弹安放/拆除的关键回合
        """
        total_rounds = demo_analysis.get("total_rounds", 0)
        kill_positions = demo_analysis.get("kill_positions", [])
        player_stats = demo_analysis.get("player_stats", {})

        if total_rounds == 0:
            return [1, 2, 3]  # 保底

        # 按回合统计击杀
        round_kills = defaultdict(list)
        for kp in kill_positions:
            rnd = self._tick_to_round(kp["tick"], demo_analysis)
            if rnd:
                round_kills[rnd].append(kp)

        # 找值得分析的回合
        candidates = []
        for rnd in range(1, total_rounds + 1):
            kills = round_kills.get(rnd, [])
            score = 0

            # 1. 残局判断：该回合击杀数少但分散
            unique_killers = set(k["killer_sid"] for k in kills)
            unique_victims = set(k["victim_sid"] for k in kills)
            if len(unique_killers) <= 2 and len(kills) >= 2:
                score += 3  # 可能的残局

            # 2. 玩家表现突出
            for sid, pstat in player_stats.items():
                player_kills = sum(1 for k in kills if k["killer_sid"] == sid)
                if player_kills >= 3:
                    score += 2  # 多杀回合
                if player_kills >= 2 and len(kills) <= 3:
                    score += 3  # 残局多杀

            # 3. 首杀/关键击杀
            headshots = sum(1 for k in kills if k.get("headshot"))
            if headshots >= 2:
                score += 1

            if score > 0:
                candidates.append((score, rnd))

        # 按得分排序，取前 5 个
        candidates.sort(key=lambda x: -x[0])

        if not candidates:
            return [1, min(4, total_rounds), min(8, total_rounds)]

        # 去重后返回
        seen = set()
        result = []
        for _, rnd in candidates:
            if rnd not in seen:
                seen.add(rnd)
                result.append(rnd)
            if len(result) >= 5:
                break

        return sorted(result)

    def _tick_to_round(self, tick: int, demo_analysis: dict) -> int:
        """tick 编号 → 回合号（粗略估算）"""
        total_kills = demo_analysis.get("total_kills", 1)
        total_rounds = demo_analysis.get("total_rounds", 1)
        kill_positions = demo_analysis.get("kill_positions", [])
        if not kill_positions:
            return 1
        # 按击杀顺序估算回合
        for i, kp in enumerate(kill_positions):
            if kp["tick"] >= tick:
                return max(1, i * total_rounds // max(len(kill_positions), 1) + 1)
        return total_rounds

    # ────────────────────────────────────────────────
    #  方法2: 分析一个回合，给出战术指导
    # ────────────────────────────────────────────────

    def analyze(self, round_context: dict) -> dict:
        """
        分析一个回合，给出战术指导。

        流程:
        1. 提取关键信息（地图、位置、武器、人数、炸弹）
        2. 查询知识库（地图战术、投掷物、经济规则）
        3. LLM 推理（综合判断）
        4. 返回结构化建议
        """
        if not round_context:
            return self._fallback_advice("数据不足")

        # ── 1. 提取信息 ──
        you = round_context.get("you", {})
        alive = round_context.get("alive_players", [])
        dead = round_context.get("dead_players", [])
        raw_map = round_context.get("map", "")
        map_name = normalize_map(raw_map)
        bomb_status = round_context.get("bomb_status", "unknown")
        time_display = round_context.get("time_display", "0:00")

        # 确定阵营和人数
        my_team = you.get("team_name", "?") if you else "?"
        enemies = [p for p in alive if p.get("team_name") and p["team_name"] != my_team]
        mates = [p for p in alive if p.get("team_name") and p["team_name"] == my_team and p.get("name") != you.get("name")]
        enemy_count = len(enemies)
        mate_count = len(mates)
        phase = f"{mate_count + 1}v{enemy_count}"

        # 玩家状态
        health = you.get("health", 100) if you else 100
        weapon = you.get("weapon", "?") if you else "?"
        position = you.get("position", {}) if you else {}
        pos_x = position.get("x", 0) if isinstance(position, dict) else 0
        pos_y = position.get("y", 0) if isinstance(position, dict) else 0

        # ── 2. 查询知识库 ──
        kb_info = self._query_knowledge(map_name, you, round_context)

        # ── 3. 构建分析 prompt ──
        prompt = self._build_analysis_prompt(
            map_name=map_name,
            phase=phase,
            health=health,
            weapon=weapon,
            enemy_count=enemy_count,
            mate_count=mate_count,
            bomb_status=bomb_status,
            time_display=time_display,
            kb_info=kb_info,
            round_context=round_context,
        )

        # ── 4. 调用 LLM 推理 ──
        advice = self._call_llm_for_advice(prompt, map_name)

        # ── 5. 结构化输出 ──
        return self._format_advice(advice, map_name, phase, health, weapon, enemy_count, kb_info)

    # ────────────────────────────────────────────────
    #  辅助方法
    # ────────────────────────────────────────────────

    def _query_knowledge(self, map_name: str, you: dict, ctx: dict) -> str:
        """查询知识库，获取地图战术信息"""
        if not self.ready:
            return ""

        pieces = []

        # 1. 地图战术
        if map_name:
            result = analyze_map(map_name, "all")
            if result.get("found"):
                for r in result["results"][:3]:
                    pieces.append(f"[{r['title']}]\n{r['content'][:300]}")

        # 2. 知识库检索
        try:
            query = f"{map_name} {ctx.get('phase', '')} 战术 残局"
            results = self.vector_store.search(query, top_k=3)
            for r in results:
                title = r["metadata"].get("title", "")
                if title and title not in "".join(pieces):
                    pieces.append(f"[{title}]\n{r['text'][:300]}")
        except Exception:
            pass

        return "\n\n".join(pieces[:4])

    def _build_analysis_prompt(self, **kwargs) -> str:
        """构建 LLM 分析 prompt"""
        map_name = kwargs["map_name"]
        phase = kwargs["phase"]
        health = kwargs["health"]
        weapon = kwargs["weapon"]
        enemy_count = kwargs["enemy_count"]
        mate_count = kwargs["mate_count"]
        bomb_status = kwargs["bomb_status"]
        time_display = kwargs["time_display"]
        kb_info = kwargs["kb_info"]
        ctx = kwargs["round_context"]

        # 敌人信息
        you = ctx.get("you", {})
        alive = ctx.get("alive_players", [])
        my_team = you.get("team_name", "?") if you else "?"
        enemies_info = []
        for p in alive:
            if p.get("team_name") and p["team_name"] != my_team:
                enemies_info.append(f"  {p.get('name','?')} HP={p.get('health','?')} 武器={p.get('weapon','?')}")

        return f"""你是一个顶尖的 CS2 战术教练。请分析以下对局情况，给出精准的战术指导。

## 当前局势
- 地图: {map_name}
- 局势: {phase}（我方 {mate_count + 1} 人 vs 敌方 {enemy_count} 人）
- 时间剩余: {time_display}
- 炸弹状态: {bomb_status}
- 你的血量: {health} | 武器: {weapon}

## 敌方存活信息
{chr(10).join(enemies_info) if enemies_info else "  未知"}

## 知识库参考
以下信息来自知识库，请结合实际情况分析：
{kb_info[:800] if kb_info else "  无"}

## 分析要求
请从以下维度给出建议，每条都要简洁具体：
1. 形势判断（优势/劣势/均势）
2. 推荐操作（具体的位置、打法）
3. 道具使用建议（如果有）
4. 敌人可能的位置
5. 常见错误提醒

用中文回答，语气专业直接。"""

    def _call_llm_for_advice(self, prompt: str, map_name: str) -> str:
        """调用 LLM 获取战术建议"""
        # 优先使用对方项目的 LLM
        if LLM_READY:
            try:
                reply, err = call_llm([
                    {"role": "system", "content": "你是一个顶尖的 CS2 战术教练，回答简洁有力。"},
                    {"role": "user", "content": prompt},
                ])
                if reply:
                    return reply
            except Exception:
                pass

        # 备用：使用我的 Agent
        if self.agent:
            try:
                return self.agent.respond(prompt)
            except Exception:
                pass

        # 兜底：规则推理
        return self._rule_based_advice(prompt, map_name)

    def _rule_based_advice(self, prompt: str, map_name: str) -> str:
        """规则兜底推理（LLM 不可用时）"""
        # 从 prompt 中提取关键信息
        lines = prompt.split("\n")
        phase = ""
        health = 100
        weapon = "?"
        enemy_count = 0
        bomb_status = "unknown"

        for line in lines:
            if "局势:" in line:
                phase = line.split("局势:")[-1].strip()
            if "血量:" in line:
                try:
                    health = int(line.split("血量:")[1].split("|")[0].strip())
                except ValueError:
                    pass
            if "武器:" in line and "你的" in line:
                weapon = line.split("武器:")[-1].strip()
            if "敌方" in line and "人" in line:
                try:
                    enemy_count = int(line.split("敌方")[1].split("人")[0].strip())
                except ValueError:
                    pass
            if "炸弹状态:" in line:
                bomb_status = line.split("炸弹状态:")[-1].strip()

        advice_parts = []

        # 形势判断
        if enemy_count == 0:
            advice_parts.append("形势: 安全，可以放松搜点")
        elif enemy_count == 1:
            advice_parts.append("形势: 1v1 残局，胜负各半")
        elif enemy_count == 2:
            advice_parts.append("形势: 1v2 劣势残局，需要利用掩体打时间差")
        else:
            advice_parts.append("形势: 绝对劣势，建议保枪或换人")

        # 血量判断
        if health < 20:
            advice_parts.append("血量极低，避免正面交火，利用掩体打游击")
        elif health < 50:
            advice_parts.append("血量偏低，尽量打远程对枪或偷侧身")

        # 炸弹判断
        if bomb_status == "planted":
            advice_parts.append("炸弹已安放，需要回防拆弹")
        elif bomb_status == "carried":
            advice_parts.append("炸弹在你方，需要找机会下包")

        # 地图通用建议
        if map_name:
            advice_parts.append(f"在{map_name}上，注意利用地图熟悉的地形做掩体")

        return "\n".join(advice_parts)

    def _format_advice(self, raw_advice: str, map_name: str, phase: str,
                       health: int, weapon: str, enemy_count: int,
                       kb_info: str) -> dict:
        """把 LLM 输出格式化为结构化建议"""
        # 难度判断
        if enemy_count == 0:
            difficulty = "easy"
        elif enemy_count == 1:
            difficulty = "medium"
        elif enemy_count == 2:
            difficulty = "hard"
        else:
            difficulty = "impossible"

        # 局势判断
        if health < 20 or enemy_count >= 3:
            assessment = f"劣势，{phase}，血量{health}"
        elif enemy_count == 0:
            assessment = f"安全，{phase}"
        elif enemy_count == 1 and health > 50:
            assessment = f"均势，{phase}，有机会"
        else:
            assessment = f"需要谨慎，{phase}，血量{health}"

        return {
            "assessment": assessment,
            "difficulty": difficulty,
            "recommended_action": raw_advice[:300],
            "position_to_hold": f"建议利用{map_name}的掩体进行防守",
            "utility_to_use": [
                {"item": "烟雾弹", "target": "关键路口", "description": "封锁敌人视线"},
                {"item": "闪光弹", "target": "敌人方向", "description": "创造进攻窗口"},
            ],
            "likely_enemy_positions": [
                f"敌人可能在{map_name}的关键位置架枪",
            ],
            "reference": "潘一鸣战术知识库",
            "alternative": "如果情况不利，可以考虑保枪",
            "common_mistake": "不要 rush，先收集信息",
        }

    def _fallback_advice(self, reason: str) -> dict:
        """数据不足时的兜底"""
        return {
            "assessment": f"数据不足 - {reason}",
            "difficulty": "unknown",
            "recommended_action": "无法分析，请检查数据是否完整",
            "position_to_hold": "未知",
            "utility_to_use": [],
            "likely_enemy_positions": [],
            "reference": "潘一鸣战术知识库",
            "alternative": "",
            "common_mistake": "",
        }


# ── 快速测试 ──
if __name__ == "__main__":
    coach = MyTacticalCoach()
    integrated = IntegratedCoach(tactical_coach=coach)

    # 尝试找 demo 文件
    demo_dir = Path("D:/SteamLibrary/steamapps/common/Counter-Strike Global Offensive/game/csgo/replays")
    if not demo_dir.exists():
        demo_dir = Path(".")  # 当前目录

    demos = list(demo_dir.glob("*.dem"))
    if demos:
        result = integrated.analyze_demo(str(demos[0]), player_filter="基666")
        player_name = result.get("player_name", "?")
        player_data = result.get("player_data", {})
        print(f"选手: {player_name}")
        print(f"数据: {player_data.get('kills', 0)}K / {player_data.get('kd', 0)} K/D")
        print()
        for ta in result.get("tactical_analysis", []):
            print(f"=== 第 {ta['round']} 回合残局分析 ===")
            print(ta["advice"]["assessment"])
            print(ta["advice"]["recommended_action"][:200])
            print()
    else:
        print("未找到 demo 文件，测试手动模式...")
        # 手动构造测试数据
        test_context = {
            "round": 4,
            "map": "de_dust2",
            "phase": "1v2",
            "time_display": "0:45",
            "you": {
                "name": "基666",
                "health": 45,
                "armor": 50,
                "has_helmet": True,
                "weapon": "ak-47",
                "position": {"x": 1250, "y": 850},
            },
            "alive_players": [
                {"name": "DONKING", "team_name": "CT", "health": 75, "weapon": "m4a4"},
                {"name": "encore", "team_name": "CT", "health": 100, "weapon": "awp"},
            ],
            "dead_players": ["队友A", "队友B"],
            "bomb_status": "planted",
            "bomb_site": "B",
            "score": {"T": 4, "CT": 3},
        }
        advice = coach.analyze(test_context)
        print(f"=== 第 4 回合残局分析 ===")
        print(f"评估: {advice['assessment']}")
        print(f"难度: {advice['difficulty']}")
        print(f"建议: {advice['recommended_action'][:200]}")
        print(f"参考: {advice['reference']}")
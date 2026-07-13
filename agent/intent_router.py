"""意图识别与路由分发"""

import re
from typing import Dict, Optional, List, Tuple


class IntentRouter:
    """基于规则+关键词的意图识别器

    识别用户提问的意图，路由到对应的处理模块：
    - knowledge_retrieval: 知识库检索（地图、投掷物、武器信息等）
    - economy_query: 经济计算
    - weapon_compare: 武器对比
    - tactical_advice: 战术建议
    - greeting: 打招呼
    - general: 其他通用问题
    """

    # 意图识别关键词规则
    INTENT_PATTERNS = {
        "economy_query": [
            r"经济", r"eco", r"强起", r"半起", r"全起", r"full\s*buy",
            r"force\s*buy", r"存钱", r"省钱", r"花多少钱", r"买什么",
            r"金钱", r"\$\d+", r"(\d+)\s*(块|元|钱|金)", r"手枪局",
            r"输局奖励", r"loss\s*bonus", r"击杀奖励", r"kill\s*reward",
            r"配装", r"装备推荐", r"budget", r"预算",
            r"eco", r"半起", r"全起", r"翻盘", r"保枪", r"发枪",
        ],
        "weapon_compare": [
            r"对比", r"比较", r"vs", r"和.*哪个好", r"哪个更强",
            r"哪个厉害", r"区别", r"不同", r"伤害对比", r"参数对比",
            r"推荐.*武器", r"选什么枪", r"用什么枪",
            r"大狙", r"连狙", r"鸟狙", r"机枪", r"微冲",
        ],
        "tactical_advice": [
            r"战术", r"怎么打", r"如何进攻", r"如何防守", r"策略",
            r"站位", r"默认", r"回防", r"前压", r"rush",
            r"残局", r"1v", r"怎么赢", r"怎么玩",
            r"eco.*(局|怎么)", r"强起.*(局|怎么)",
            r"夹", r"爆弹", r"假打", r"转点", r"一波",
            r"A大", r"A小", r"B大", r"B小", r"中路", r"香蕉道",
            r"警家", r"匪家", r"拱门", r"连接", r"下水道",
            r"进攻", r"防守", r"怎么攻", r"怎么守",
        ],
        "map_query": [
            r"地图", r"点位", r"报点", r"callout", r"地图分析",
            r"mirage", r"dust2", r"inferno", r"nuke", r"ancient",
            r"anubis", r"overpass", r"vertigo",
            r"米垃圾", r"沙二", r"沙漠", r"沙城", r"小镇", r"迷城",
            r"核子", r"遗迹", r"游乐园", r"大厦", r"阿努比斯",
        ],
        "grenade_query": [
            r"烟(雾|幕)?弹", r"闪光弹", r"手雷", r"高爆", r"燃烧弹",
            r"莫洛托夫", r"投掷物", r"smoke", r"flash", r"molotov",
            r"fire", r"incendiary", r"he\s*grenade",
            r"怎么丢", r"怎么扔", r"投掷",
            # 中文简称：烟、闪、火、雷
            r"(丢|扔|封|给|要|用).*(烟|闪|火|雷|诱饵)",
            r"烟(位|点|封|怎么)", r"闪(光|怎么|位)", r"火(怎么|位|烧)",
            r"单向烟", r"反弹闪", r"popflash", r"燃烧弹",
            r"道具", r"投掷", r"线位", r"瞄点",
        ],
        "weapon_query": [
            r"枪械", r"武器", r"步枪", r"冲锋枪", r"狙击", r"手枪",
            r"参数", r"伤害", r"后坐力", r"弹道", r"穿甲",
            r"ak", r"m4", r"awp", r"deagle", r"沙漠之鹰",
            r"famas", r"galil", r"sg553", r"aug", r"p90",
            r"mac.?10", r"mp9", r"usp", r"glock", r"p250",
            r"fiveseven", r"tec.?9",
            # 中文俗称
            r"大狙", r"鸟狙", r"连狙", r"微冲", r"车王", r"吹风机",
            r"野牛", r"咖喱", r"法玛斯", r"内格夫",
        ],
        "greeting": [
            r"你好", r"嗨", r"hi", r"hello", r"^hey", r"早上好",
            r"晚上好", r"下午好", r"你是谁", r"能做什么",
        ],
    }

    def __init__(self):
        # 编译正则表达式
        self.compiled_patterns = {}
        for intent, patterns in self.INTENT_PATTERNS.items():
            self.compiled_patterns[intent] = [re.compile(p, re.IGNORECASE) for p in patterns]

    def classify(self, user_input: str) -> str:
        """识别用户输入意图

        Returns:
            意图标签
        """
        # 优先匹配具体意图
        scores = {}
        for intent, patterns in self.compiled_patterns.items():
            score = sum(1 for p in patterns if p.search(user_input))
            if score > 0:
                scores[intent] = score

        if not scores:
            return "general"

        # 返回得分最高的意图
        best_intent = max(scores, key=scores.get)
        return best_intent

    def extract_entities(self, user_input: str) -> Dict:
        """从用户输入中提取实体信息

        提取内容：地图名、武器名、阵营、金钱数等
        """
        entities = {}
        text = user_input.lower()

        # 提取地图
        maps = {
            # 英文标准名
            "mirage": "Mirage", "dust2": "Dust2", "inferno": "Inferno",
            "nuke": "Nuke", "ancient": "Ancient", "anubis": "Anubis",
            "overpass": "Overpass", "vertigo": "Vertigo",
            # 中文标准名
            "荒漠迷城": "Mirage", "炙热沙城": "Dust2", "炼狱小镇": "Inferno",
            "核子危机": "Nuke", "远古遗迹": "Ancient", "阿努比斯": "Anubis",
            "死亡游乐园": "Overpass", "眩晕大厦": "Vertigo",
            # 中文俗称
            "米垃圾": "Mirage", "迷城": "Mirage",
            "沙二": "Dust2", "沙漠": "Dust2", "沙城": "Dust2", "dust": "Dust2",
            "小镇": "Inferno",
            "核子": "Nuke", "核弹": "Nuke",
            "遗迹": "Ancient",
            "游乐园": "Overpass", "乐园": "Overpass",
            "大厦": "Vertigo",
        }
        for key, name in maps.items():
            if key in text:
                entities["map"] = name
                break

        # 提取地图点位（中文称呼）
        callouts_found = []
        callout_patterns = {
            "A大": "A Long", "A大道": "A Long",
            "A小": "A Short", "A小道": "A Short",
            "B大": "B Long", "B大道": "B Long",
            "B小": "B Short", "B小道": "B Short",
            "警家": "CT Spawn",
            "匪家": "T Spawn",
            "香蕉道": "Banana",
            "拱门": "Arch",
            "连接": "Connector",
            "下水道": "Underpass",
            "二楼": "Balcony",
            "井": "Pit",
            "坑": "Pit",
            "车位": "Car",
            "沙袋": "Sandbags",
            "教堂": "Church",
            "书房": "Library",
            "墓地": "Graveyard",
            "超市": "Market",
            "跳台": "Balcony",
            "管道": "Vents",
            "外场": "Outside",
            "铁板": "Ramp",
            "黄房": "Yellow",
            "红箱": "Red",
            "蓝箱": "Default",
            "三箱": "Triple",
            "棺材": "Coffins",
            "忍者位": "Ninja",
            "后花园": "Back Plat",
            "A包点": "A Site", "B包点": "B Site",
            "包点": "Site",
            "狗洞": "Squeaky",
            "B洞": "B Tunnel",
            "A洞": "A Long",
            "中门": "Middle Doors",
            "小道": "Short",
            "大道": "Long",
        }
        for cn, en in callout_patterns.items():
            if cn in text:
                callouts_found.append(f"{cn}({en})")
        if callouts_found:
            entities["callouts"] = callouts_found

        # 提取投掷物类型（中文简称）
        grenade_types = []
        if re.search(r'(烟|烟雾|烟雾弹)', text):
            grenade_types.append("smoke")
        if re.search(r'(闪|闪光|闪光弹)', text):
            grenade_types.append("flash")
        if re.search(r'(火|燃烧|燃烧弹|莫洛托夫)', text):
            grenade_types.append("fire")
        if re.search(r'(雷|手雷|高爆|炸)', text):
            grenade_types.append("he")
        if grenade_types:
            entities["grenades"] = grenade_types

        # 提取阵营
        if any(w in text for w in ["t侧", "t方", "匪", "进攻方", "t "]):
            entities["side"] = "T"
        elif any(w in text for w in ["ct侧", "ct方", "警", "防守方", "ct "]):
            entities["side"] = "CT"

        # 提取金钱
        money_match = re.search(r'\$?(\d{3,5})\s*(块|元|钱|金)?', text)
        if money_match:
            entities["money"] = int(money_match.group(1))

        # 提取武器（含中文俗称）
        weapons = {
            "ak-47": "AK-47", "ak47": "AK-47", "ak": "AK-47",
            "m4a4": "M4A4", "m4a1-s": "M4A1-S", "m4a1s": "M4A1-S",
            "awp": "AWP", "deagle": "Desert Eagle", "沙漠之鹰": "Desert Eagle",
            "famas": "FAMAS", "galil": "Galil AR", "sg553": "SG 553", "aug": "AUG",
            "mac-10": "MAC-10", "mac10": "MAC-10", "mp9": "MP9", "p90": "P90",
            "usp-s": "USP-S", "usp": "USP-S", "glock": "Glock-18",
            "p250": "P250", "fiveseven": "Five-SeveN", "tec-9": "Tec-9",
            # 中文俗称
            "大狙": "AWP", "鸟狙": "SSG 08", "连狙": "SSG 08",
            "车王": "MP7", "吹风机": "MAC-10", "野牛": "PP-Bizon",
            "咖喱": "Galil AR", "法玛斯": "FAMAS", "内格夫": "Negev",
            "双枪": "Dual Berettas", "沙鹰": "Desert Eagle",
            "连喷": "XM1014", "单喷": "MAG-7",
        }
        for key, name in weapons.items():
            if key in text:
                if "weapons" not in entities:
                    entities["weapons"] = []
                if name not in entities["weapons"]:
                    entities["weapons"].append(name)

        # 提取回合数
        round_match = re.search(r'第\s*(\d+)\s*局', text)
        if round_match:
            entities["round"] = int(round_match.group(1))

        # 提取连续输局
        loss_match = re.search(r'连续输\s*(\d+)\s*局', text)
        if loss_match:
            entities["consecutive_losses"] = int(loss_match.group(1))

        return entities

    def analyze(self, user_input: str) -> Dict:
        """完整分析用户输入：意图 + 实体"""
        return {
            "intent": self.classify(user_input),
            "entities": self.extract_entities(user_input),
            "raw_input": user_input,
        }


# 全局单例
_router: Optional[IntentRouter] = None


def get_router() -> IntentRouter:
    """获取全局意图识别器"""
    global _router
    if _router is None:
        _router = IntentRouter()
    return _router
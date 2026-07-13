"""CS2 战术问答 Agent 主工作流

核心流程：用户提问 → 意图识别 → 路由分发（知识库检索/工具调用/LLM 整合）→ 输出回答
"""

import os
from typing import Dict, Optional, List
from openai import OpenAI

from config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL_NAME
from .intent_router import get_router
from .memory import get_memory
from knowledge_base.vector_store import get_vector_store
from tools import TOOL_REGISTRY, call_tool


# ============== System Prompt ==============
SYSTEM_PROMPT = """你是一个专业的 CS2（反恐精英 2）战术问答助手，名叫「CS2 战术大师」。

## 你的能力
1. 回答 CS2 地图点位、战术策略、投掷物教程等问题
2. 计算经济状况并给出购买建议
3. 对比武器参数，推荐最佳装备
4. 提供多轮对话上下文支持

## 行为准则
- 回答必须准确、专业，基于知识库和工具结果
- 如果知识库中没有相关信息，诚实地告诉用户不知道
- 对于经济计算、武器对比等问题，优先使用工具计算
- 回答要简洁清晰，适当使用分段和列表

## 知识库检索结果
当用户提出具体问题时，你会收到知识库检索结果作为参考。
请基于这些结果回答问题，不要编造数据。

## 工具调用结果
当需要经济计算、武器对比时，你会收到工具调用结果。
请基于工具结果给出回答和建议。

## 对话上下文
以下是当前对话的上下文信息，请据此保持对话的连贯性。
"""


class CS2Agent:
    """CS2 战术问答 Agent"""

    def __init__(self):
        self.router = get_router()
        self.memory = get_memory()
        self.vector_store = get_vector_store()
        self.llm = OpenAI(
            api_key=LLM_API_KEY,
            base_url=LLM_BASE_URL,
        )

    def _build_messages(self, user_input: str) -> List[Dict]:
        """构建 LLM 对话消息"""
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        # 添加上文轮对话历史（最近 3 轮）
        context = self.memory.get_recent_context(3)
        for msg in context:
            messages.append({"role": msg["role"], "content": msg["content"]})

        # 添加当前用户输入
        messages.append({"role": "user", "content": user_input})
        return messages

    def _retrieve_knowledge(self, query: str, intent: str) -> str:
        """检索知识库（向量搜索 + 关键词匹配双通道）"""
        # 通道1: 向量搜索
        results = self.vector_store.search(query, top_k=5)

        # 通道2: 关键词匹配（弥补本地嵌入模型对中文支持不足）
        keyword_results = self._keyword_match(query)

        # 合并结果（去重）
        seen_ids = set()
        combined = []

        for r in results:
            tid = r["metadata"].get("title", "")
            if tid not in seen_ids and r.get("score", 2) < 1.5:
                seen_ids.add(tid)
                combined.append(r)

        for r in keyword_results:
            tid = r["metadata"].get("title", "")
            if tid not in seen_ids:
                seen_ids.add(tid)
                combined.append(r)

        if not combined:
            return ""

        context_parts = ["【知识库检索结果】"]
        for i, r in enumerate(combined, 1):
            title = r["metadata"].get("title", "")
            category = r["metadata"].get("category", "")
            context_parts.append(f"[{i}] {title}（{category}）\n{r['text'][:500]}")

        return "\n\n".join(context_parts)

    def _keyword_match(self, query: str) -> list:
        """基于关键词的本地知识匹配（弥补向量检索对中文的不足）"""
        from knowledge_base.data_loader import get_all_knowledge
        all_knowledge = get_all_knowledge()
        q = query.lower()

        # 关键词评分
        scored = []
        for item in all_knowledge:
            score = 0
            content = item["content"].lower()
            title = item["title"].lower()

            # 精确匹配标题
            if any(word in q for word in title.split()):
                score += 3

            # 内容关键词匹配
            keywords = ["回防", "防守", "进攻", "战术", "烟雾弹", "闪光弹",
                        "燃烧弹", "经济", "站位", "A点", "B点", "中路",
                        "香蕉道", "A大", "A小", "B大", "B小",
                        "mirage", "dust2", "inferno", "沙二", "米垃圾", "小镇"]
            for kw in keywords:
                if kw in q and kw in content:
                    score += 2
                if kw in q and kw in title:
                    score += 3

            # 地图匹配
            maps = {"mirage": "Mirage", "dust2": "Dust2", "inferno": "Inferno",
                    "沙二": "Dust2", "米垃圾": "Mirage", "小镇": "Inferno",
                    "沙漠": "Dust2", "迷城": "Mirage"}
            for alias, map_name in maps.items():
                if alias in q and item.get("map", "") == map_name:
                    score += 2

            if score > 0:
                scored.append((score, {
                    "text": item["content"],
                    "metadata": {
                        "title": item["title"],
                        "category": item.get("category", ""),
                        "map": item.get("map", ""),
                    },
                    "score": 0,
                }))

        # 按评分排序，返回前 3 条
        scored.sort(key=lambda x: -x[0])
        return [r for _, r in scored[:3]]

    def _execute_tools(self, intent: str, entities: Dict, user_input: str) -> str:
        """根据意图执行工具调用

        Returns:
            工具执行结果文本
        """
        tool_results = []

        if intent == "economy_query":
            # 经济计算
            money = entities.get("money", 4000)
            side = entities.get("side", "T")
            round_num = entities.get("round", 3)
            losses = entities.get("consecutive_losses", 1)

            result = call_tool("economy_calculator",
                team=side, current_money=money,
                round_number=round_num, consecutive_losses=losses)
            tool_results.append(f"【经济计算工具结果】\n{result['advice']}\n{result['specific_equipment']}")

            # 检查是否包含武器推荐
            if "推荐" in user_input or "买什么" in user_input or "配装" in user_input:
                budget = money + (1900 if losses > 0 else 3250)
                weapon_rec = call_tool("weapon_recommend",
                    budget=min(budget, 5000), side=side, play_style="all_round")
                tool_results.append(f"【武器推荐工具结果】\n{weapon_rec}")

        elif intent == "weapon_compare":
            weapons = entities.get("weapons", [])
            if weapons:
                if len(weapons) >= 2:
                    result = call_tool("weapon_compare", weapon_names=weapons)
                else:
                    result = call_tool("weapon_compare", weapon_names=weapons)
                tool_results.append(f"【武器对比工具结果】\n{result}")

            # 如果提到了预算，也推荐武器
            if "money" in entities:
                side = entities.get("side", "T")
                rec = call_tool("weapon_recommend",
                    budget=entities["money"], side=side, play_style="all_round")
                tool_results.append(f"【武器推荐工具结果】\n{rec}")

        elif intent == "tactical_advice":
            map_name = entities.get("map") or self.memory.context.get("current_map") or "Mirage"
            side = entities.get("side") or self.memory.context.get("current_side") or "T"
            result = call_tool("tactical_advice",
                map_name=map_name, side=side, situation=user_input)
            tool_results.append(f"【战术建议工具结果】\n{result}")

        elif intent == "map_query":
            map_name = entities.get("map") or "Mirage"
            result = call_tool("map_analyze", map_name=map_name, topic="all")
            if result["found"]:
                for r in result["results"]:
                    tool_results.append(f"【{r['title']}】\n{r['content'][:600]}")
            else:
                tool_results.append(result["message"])

        return "\n\n".join(tool_results)

    def _call_llm(self, messages: List[Dict]) -> str:
        """调用大语言模型"""
        try:
            response = self.llm.chat.completions.create(
                model=LLM_MODEL_NAME,
                messages=messages,
                temperature=0.7,
                max_tokens=1024,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"LLM 调用失败：{str(e)}。请检查 API 配置。"

    def _fallback_respond(self, intent: str, knowledge: str, tool_results: str) -> str:
        """当 LLM 不可用时，使用规则兜底生成回答"""
        if tool_results:
            return f"【工具计算结果】\n{tool_results}\n\n（如需更多信息，请配置 LLM API 后获得更详细的回答）"
        if knowledge:
            return f"【知识库检索结果】\n{knowledge[:800]}\n\n（如需更智能的回答，请配置 LLM API）"
        return "请配置 LLM API（在 .env 文件中设置 LLM_API_KEY）以获得完整的智能问答体验。"

    def respond(self, user_input: str) -> str:
        """处理用户输入并返回回答

        Args:
            user_input: 用户输入文本

        Returns:
            Agent 回答
        """
        # 1. 意图识别
        analysis = self.router.analyze(user_input)
        intent = analysis["intent"]
        entities = analysis["entities"]

        # 2. 更新记忆
        self.memory.add_turn("user", user_input)
        self.memory.update_context(user_input)

        # 3. 知识库检索
        knowledge = self._retrieve_knowledge(user_input, intent)

        # 4. 工具调用
        tool_results = self._execute_tools(intent, entities, user_input)

        # 5. 构建 LLM 消息
        messages = self._build_messages(user_input)

        # 在用户消息后面添加知识库和工具结果
        enhanced_input = user_input
        if knowledge:
            enhanced_input += f"\n\n{knowledge}"
        if tool_results:
            enhanced_input += f"\n\n{tool_results}"

        # 添加上下文摘要
        context_summary = self.memory.get_context_summary()
        if context_summary:
            enhanced_input += f"\n\n对话上下文：{context_summary}"

        # 替换最后一条用户消息
        messages[-1] = {"role": "user", "content": enhanced_input}

        # 6. 调用 LLM
        try:
            response = self._call_llm(messages)
        except Exception:
            response = self._fallback_respond(intent, knowledge, tool_results)

        # 7. 更新记忆
        self.memory.add_turn("assistant", response)
        self.memory.context["last_topic"] = intent

        return response


# 全局单例
_agent: Optional[CS2Agent] = None


def get_agent() -> CS2Agent:
    """获取全局 Agent 实例"""
    global _agent
    if _agent is None:
        _agent = CS2Agent()
    return _agent
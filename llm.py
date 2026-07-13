""" LLM 调用 — LangChain 版本 """

from config import model, LLM_API_BASE, LLM_MODEL

from langchain_core.messages import HumanMessage, SystemMessage, AIMessage


def call_llm(messages, temperature=0.7, max_tokens=2048):
    """连续对话（传入 LangChain 消息列表）"""
    try:
        # messages 可以是 LangChain 对象列表，也可以是普通 dict 列表
        # 统一处理
        langchain_msgs = []
        for m in messages:
            if isinstance(m, dict):
                role = m.get("role", "user")
                content = m.get("content", "")
                if role == "system":
                    langchain_msgs.append(SystemMessage(content=content))
                elif role == "assistant":
                    langchain_msgs.append(AIMessage(content=content))
                else:
                    langchain_msgs.append(HumanMessage(content=content))
            else:
                langchain_msgs.append(m)

        reply = model.invoke(langchain_msgs)
        return reply.content, None
    except Exception as e:
        return None, f"LLM 调用失败: {e}"


def call_llm_with_tools(messages, tools, temperature=0.7, max_tokens=4096):
    """调用 LLM 并支持工具调用（@tool 装饰器函数列表）"""
    try:
        langchain_msgs = []
        for m in messages:
            if isinstance(m, dict):
                role = m.get("role", "user")
                content = m.get("content", "")
                if role == "system":
                    langchain_msgs.append(SystemMessage(content=content))
                elif role == "assistant":
                    langchain_msgs.append(AIMessage(content=content))
                else:
                    langchain_msgs.append(HumanMessage(content=content))
            else:
                langchain_msgs.append(m)

        # 绑定 tools
        model_with_tools = model.bind_tools(tools)
        reply = model_with_tools.invoke(langchain_msgs)

        # 如果有 tool calls
        if reply.tool_calls:
            for tc in reply.tool_calls:
                func_name = tc["name"]
                args = tc["args"]

                # 找到对应的函数并执行
                for tool_fn in tools:
                    if tool_fn.name == func_name:
                        result = tool_fn.invoke(args)
                        langchain_msgs.append(AIMessage(content=reply.content) if reply.content else None)
                        langchain_msgs.append(result)
                        break

            # 把工具结果发回 LLM
            final_reply = model_with_tools.invoke(langchain_msgs)
            return final_reply.content, None

        return reply.content, None
    except Exception as e:
        return None, f"LLM 调用失败: {e}"


def call_llm_one_shot(prompt_text, system=None):
    """单次简单调用"""
    msgs = []
    if system:
        msgs.append({"role": "system", "content": system})
    msgs.append({"role": "user", "content": prompt_text})
    return call_llm(msgs)


def get_embedding(text):
    """获取文本向量嵌入"""
    import requests
    key = LLM_API_KEY
    if not key:
        return None, "未配置 API Key"
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "text-embedding-v2",
        "input": text,
    }
    try:
        url = LLM_API_BASE.rstrip("/") + "/embeddings"
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()["data"][0]["embedding"], None
    except Exception as e:
        return None, f"Embedding 失败: {e}"

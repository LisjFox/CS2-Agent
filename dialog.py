""" 对话模式 — with LangChain + @tool """

import sys

from analysis import build_system_prompt
from llm import call_llm, call_llm_with_tools
from memory import load_memory, save_memory, get_history, format_history, \
    add_session, manage_short_term
from tools import TOOL_LIST
from config import LLM_API_KEY

TOOLS = TOOL_LIST


def dialog_loop(coach_data, player_name, llm_response=None, err=None,
               round_data=None, demo_name=""):
    """进入对话模式，用户可连续和 AI 教练聊天。"""
    memory = load_memory()
    add_session(memory, player_name, coach_data, llm_response,
                demo_name=demo_name)

    history = get_history(memory, player_name)
    history_text = format_history(history, limit=5) if history else ""

    system_prompt = build_system_prompt(coach_data, history_text,
                                       round_data=round_data,
                                       player_name=player_name)
    messages = [{"role": "system", "content": system_prompt}]
    if llm_response:
        messages.append({"role": "assistant", "content": llm_response[:1500]})

    print(f"\n{'='*55}")
    print(f"  CS2 AI Coach -- 对话模式 (LangChain)")
    print(f"  {player_name}: {coach_data['kills']}K/{coach_data['deaths']}D "
          f"K/D {coach_data['kd']} HS% {coach_data['hs_pct']}%")
    if not LLM_API_KEY:
        print(f"  [提示] 请在 config.py 中配置 LLM_API_KEY")
    else:
        print(f"  工具: 历史查询 / 趋势分析 / 训练计划 / 武器建议")
    print(f"{'='*55}")
    print("输入问题开始交流，或输入命令:")
    print("  history  -- 查看历史记录")
    print("  save     -- 保存")
    print("  exit     -- 退出")
    print()

    while True:
        try:
            q = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n已退出")
            break

        if not q:
            continue
        if q.lower() in ("exit", "quit", "q"):
            print("再见! 继续练枪!")
            break
        if q.lower() == "save":
            save_memory(memory)
            import memory as mem_mod
            print("已保存到 " + str(mem_mod.MEMORY_FILE))
            continue
        if q.lower() == "history":
            h = format_history(history, limit=10)
            print(f"\n-- 历史记录 --\n{h}\n")
            continue
        if q.lower() in ("help", "?"):
            print("命令: history / save / exit")
            continue

        if not LLM_API_KEY:
            print("[请在 config.py 中配置 LLM_API_KEY]")
            continue

        messages.append({"role": "user", "content": q})
        print("[AI] ", end="", flush=True)

        # 使用带 tools 的调用
        reply, chat_err = call_llm_with_tools(messages, TOOLS)

        if chat_err:
            # 降级到普通调用
            reply, chat_err2 = call_llm(messages)
            if chat_err2:
                print(f"\n[错误] {chat_err2}")
                messages.pop()
                continue

        print(reply)
        messages.append({"role": "assistant", "content": reply})
        messages = manage_short_term(messages)
        print()

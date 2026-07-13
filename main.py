#!/usr/bin/env python3
"""
CS2 Agent — 主入口
===================
解析 CS2 Demo，生成可视化报告，进入 AI 教练对话。

使用:
    python main.py --latest --player "基666"
    python main.py path/to/demo.dem
    python main.py --no-dialog
    python main.py --history
"""

import sys
import argparse
from pathlib import Path

from config import LLM_API_KEY
from parser import parse_demo
from analysis import build_coach_data, build_prompt
from llm import call_llm_one_shot
from report import generate_html
from memory import load_memory, get_history, format_history
from dialog import dialog_loop


_MAPS_DOWNLOADED = False  # only try once


def ensure_maps(map_name):
    """确保地图雷达图已下载."""
    global _MAPS_DOWNLOADED
    from awpy.data import MAPS_DIR
    if _MAPS_DOWNLOADED:
        return
    test = MAPS_DIR / f"{map_name}.png"
    if test.exists():
        _MAPS_DOWNLOADED = True
        return
    from awpy.data.utils import create_data_dir_if_not_exists, fetch_resource
    create_data_dir_if_not_exists()
    try:
        fetch_resource("maps", 17595823)
    except Exception:
        pass
    _MAPS_DOWNLOADED = True


def find_replays():
    """自动找 CS2 replays 目录。
    优先读 Steam 注册表，再扫描所有 Steam 库目录。
    """
    import winreg

    # 1) 从注册表读 Steam 安装路径
    steam_path = None
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                            r"Software\Valve\Steam") as key:
            steam_path = Path(winreg.QueryValueEx(key, "SteamPath")[0])
    except Exception:
        pass

    candidates = []

    if steam_path and steam_path.exists():
        # 2) 读 libraryfolders.vdf 找到所有 Steam 库
        lf = steam_path / "steamapps" / "libraryfolders.vdf"
        if lf.exists():
            text = lf.read_text("utf-8", errors="ignore")
            import re
            for m in re.finditer(r'"path"\s+"([^"]+)"', text):
                candidates.append(Path(m.group(1)) / "steamapps" / "common" /
                                  "Counter-Strike Global Offensive" / "game" / "csgo" / "replays")
        # 3) 默认库目录
        candidates.append(steam_path / "steamapps" / "common" /
                          "Counter-Strike Global Offensive" / "game" / "csgo" / "replays")

    # 4) 回退：常见路径
    fallbacks = [
        Path.home() / "Documents/csgo",
        Path("D:/SteamLibrary/steamapps/common/Counter-Strike Global Offensive/game/csgo/replays"),
        Path("C:/Program Files (x86)/Steam/steamapps/common/Counter-Strike Global Offensive/game/csgo/replays"),
    ]
    for d in candidates + fallbacks:
        if d.exists():
            return d
    return None


def main():
    parser = argparse.ArgumentParser(description="CS2 Agent — 解析 Demo + AI 教练分析")
    parser.add_argument("demo", nargs="?", help=".dem 文件路径")
    parser.add_argument("--player", default=None, help="要高亮的玩家名")
    parser.add_argument("--latest", action="store_true", help="自动找最近 Demo")
    parser.add_argument("--output", "-o", default=None, help="报告输出路径")
    parser.add_argument("--no-dialog", action="store_true", help="跳过对话模式")
    parser.add_argument("--history", action="store_true", help="查看历史记录")
    args = parser.parse_args()

    # --- history mode ---
    if args.history:
        mem = load_memory()
        if args.player:
            s = get_history(mem, args.player)
            if s:
                print(f"  {args.player} 的历史记录:")
                for sess in s[-20:]:
                    print(f"  [{sess['date']}] {sess['kills']}K/{sess['deaths']}D  "
                          f"K/D {sess['kd']}  HS% {sess['hs_pct']}%")
            else:
                print(f"无 {args.player} 的历史记录")
        else:
            print("所有玩家:")
            for name, pdata in mem["players"].items():
                last = pdata["sessions"][-1] if pdata["sessions"] else {}
                print(f"  {name}: {len(pdata['sessions'])} games, "
                      f"last: {last.get('kills',0)}K/{last.get('deaths',0)}D")
        return

    # --- find demo ---
    demo_path = args.demo
    if not demo_path and args.latest:
        replays = find_replays()
        if replays:
            demos = sorted(replays.glob("*.dem"), key=lambda p: p.stat().st_mtime, reverse=True)
            if demos:
                demo_path = demos[0]
                print(f"自动找到: {demo_path}")

    if not demo_path:
        parser.print_help()
        print("\n错误: 请指定 .dem 文件，或使用 --latest")
        sys.exit(1)

    # --- 1. parse ---
    print("[1/4] 解析 Demo...")
    data = parse_demo(demo_path)
    print(f"      地图: {data['map_name']} | 击杀: {data['total_kills']} | 回合: {data['total_rounds']}")
    ensure_maps(data["map_name"])

    # --- player selection ---
    player_sid = None
    if args.player:
        for sid, p in data["player_stats"].items():
            if args.player in p["name"]:
                player_sid = sid
                break
    if not player_sid:
        player_sid = max(data["player_stats"].keys(),
                         key=lambda sid: data["player_stats"][sid]["kills"])
    player_name = data["player_stats"][player_sid]["name"]

    # --- 2. coach data ---
    coach_data = build_coach_data(data, player_sid)
    print(f"      高亮: {player_name} ({coach_data['kills']}K, {coach_data['kd']} K/D)")

    # --- 3. LLM ---
    prompt_text = build_prompt(coach_data)
    llm_response = None
    err = None

    if LLM_API_KEY:
        print("[2/4] 调用 LLM...")
        llm_response, err = call_llm_one_shot(
            prompt_text,
            system="你是 CS2 专业教练，分析数据并给出训练建议。"
        )
        if err:
            print(f"      [警告] {err}")
        else:
            print("      LLM 分析完成")
    else:
        err = "请在 config.py 中配置 LLM_API_KEY"

    # save prompt for reference
    prompt_path = Path(demo_path).parent / f"{Path(demo_path).stem}_coach_prompt.txt"
    prompt_path.write_text(prompt_text, encoding="utf-8")

    # --- 4. report ---
    print("[3/4] 生成 HTML 报告...")
    output = args.output or str(Path(demo_path).parent / f"{Path(demo_path).stem}_report.html")
    report_path = generate_html(data, coach_data, llm_response, player_name, player_sid, output)
    print(f"      报告: {report_path}")

    # --- summary ---
    print(f"\n{'='*50}")
    print(f"  {player_name}: {coach_data['kills']}K / {coach_data['deaths']}D / "
          f"K/D {coach_data['kd']} / HS% {coach_data['hs_pct']}")
    print(f"  武器: {coach_data['top_weapon']} ({coach_data['top_weapon_kills']})")
    print(f"  报告: {report_path}")
    print(f"{'='*50}")

    # --- 5. dialog ---
    if not args.no_dialog:
        print("\n[4/4] 进入对话模式...")
        try:
            demo_name = Path(demo_path).name
            dialog_loop(coach_data, player_name, llm_response, err,
                       round_data=data.get("round_data", {}),
                       demo_name=demo_name)
        except Exception as e:
            print(f"[对话异常] {e}")


if __name__ == "__main__":
    main()

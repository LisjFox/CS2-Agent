"""测试队友代码合并结果"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

from integration.pan_coach import MyTacticalCoach
from integration import IntegratedCoach
from parser import parse_demo
from snapshot import DemoSnapshot

print("=== 测试合体效果 ===")
coach = MyTacticalCoach()
integrated = IntegratedCoach(tactical_coach=coach)

demo_dir = Path("D:/SteamLibrary/steamapps/common/Counter-Strike Global Offensive/game/csgo/replays")
demos = list(demo_dir.glob("*.dem"))
if not demos:
    print("无 demo 文件")
    sys.exit(1)

# 1. 解析数据
data = parse_demo(str(demos[0]))
player_sid = max(data["player_stats"].keys(), key=lambda s: data["player_stats"][s]["kills"])
player_name = data["player_stats"][player_sid]["name"]
print(f"\n选手: {player_name}")
print(f"数据: {data['total_kills']}总击杀 / {data['total_rounds']}回合")

# 2. 找残局回合
clutch = coach.find_clutch_rounds(data)
print(f"\n潘一鸣找出的值得分析的回合: {clutch}")

# 3. 分析第一个残局回合
snap = DemoSnapshot(str(demos[0]))
rnd = clutch[0] if clutch else 1
state = snap.get_tick_state(rnd, 30)

# 构建上下文
you = None
for p in state.get("all_players", []):
    if p["name"] == player_name:
        you = p
        break

alive = [p for p in state.get("all_players", []) if p["health"] > 0]
context = {
    "round": rnd,
    "map": state.get("map", ""),
    "phase": "analysis",
    "time_display": state.get("time_display", ""),
    "you": you,
    "alive_players": alive,
    "dead_players": [p["name"] for p in state.get("all_players", []) if p["health"] == 0],
    "bomb_status": "unknown",
    "bomb_site": "",
}

# 4. 战术分析
advice = coach.analyze(context)
print(f"\n=== 第 {rnd} 回合战术分析 ===")
print(f"评估: {advice['assessment']}")
print(f"难度: {advice['difficulty']}")
print(f"建议: {advice['recommended_action'][:200]}")
if advice.get("likely_enemy_positions"):
    print(f"敌人位置: {advice['likely_enemy_positions'][0]}")
print(f"参考: {advice['reference']}")
print("\n[OK] 合体成功!")

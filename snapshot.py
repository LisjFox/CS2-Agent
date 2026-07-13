"""
Demo 时刻快照 — 从 .dem 文件提取指定时刻的完整对局状态
====================================================

用法:
    from snapshot import DemoSnapshot

    snap = DemoSnapshot("match.dem")
    state = snap.get_tick_state(round_num=4, time_sec=97)
    # 返回该时刻所有玩家的位置/血量/武器/道具/经济
"""

from pathlib import Path
from awpy import Demo


class DemoSnapshot:
    """Demo 时刻快照提取器."""

    def __init__(self, demo_path):
        self.path = Path(demo_path)
        self.demo = Demo(str(self.path))
        self.map_name = self.demo.header["map_name"]
        self.tickrate = self.demo.header.get("tickrate", 64)

        # 解析回合开始事件
        self.round_starts = self.demo.parser.parse_event("round_start")
        self.player_info = self.demo.parser.parse_player_info()

        # 可用字段列表
        self.tick_fields = [
            "X", "Y", "Z",
            "health", "armor", "team_num",
            "active_weapon", "current_equip_value",
        ]

    def round_to_tick(self, round_num):
        """第 N 回合开始时的 tick 编号."""
        if round_num < 1 or round_num > len(self.round_starts):
            raise ValueError(f"只有 {len(self.round_starts)} 个回合，没有第 {round_num} 回合")
        return int(self.round_starts.iloc[round_num - 1]["tick"])

    def get_tick_state(self, round_num, time_sec):
        """提取指定（回合, 时间点）的全场状态.

        Args:
            round_num: 第几回合（从 1 开始）
            time_sec: 回合开始后的秒数

        Returns:
            dict: 包含该时刻所有玩家的状态
        """
        target_tick = self._resolve_tick(round_num, time_sec)

        # 提取所有玩家的状态
        tick_data = self.demo.parser.parse_ticks(self.tick_fields, ticks=[target_tick])

        if tick_data.empty:
            return {"error": f"tick {target_tick} 无数据", "tick": target_tick}

        # 按玩家整理
        players = []
        for _, row in tick_data.iterrows():
            player = {
                "name": row.get("name", "?"),
                "steamid": str(row.get("steamid", "")),
                "team": int(row["team_num"]) if row["team_num"] else None,
                "team_name": {2: "T", 3: "CT"}.get(int(row["team_num"]), "?") if row["team_num"] else "?",
                "health": int(row["health"]) if row["health"] and row["health"] > 0 else 0,
                "armor": int(row["armor"]) if row["armor"] else 0,
                "position": {
                    "x": round(float(row["X"]), 1) if row["X"] else 0,
                    "y": round(float(row["Y"]), 1) if row["Y"] else 0,
                    "z": round(float(row["Z"]), 1) if row["Z"] else 0,
                },
                "equip_value": int(row["current_equip_value"]) if row["current_equip_value"] else 0,
            }

            # 用装备价值估算武器类型
            eq = player["equip_value"]
            if eq >= 3700:
                player["weapon"] = "步枪 (AK/M4/AWP)"
            elif eq >= 2500:
                player["weapon"] = "步枪/冲锋枪"
            elif eq >= 1500:
                player["weapon"] = "冲锋枪/手枪"
            else:
                player["weapon"] = "手枪/刀"

            players.append(player)

        # 按阵营分组
        t_alive = [p for p in players if p["team"] == 2 and p["health"] > 0]
        t_dead = [p for p in players if p["team"] == 2 and p["health"] == 0]
        ct_alive = [p for p in players if p["team"] == 3 and p["health"] > 0]
        ct_dead = [p for p in players if p["team"] == 3 and p["health"] == 0]

        return {
            "map": self.map_name,
            "tick": target_tick,
            "round": round_num,
            "time_sec": time_sec,
            "time_display": self._format_time(time_sec),
            "t_alive": t_alive,
            "ct_alive": ct_alive,
            "t_dead": t_dead,
            "ct_dead": ct_dead,
            "all_players": players,
        }

    def _resolve_tick(self, round_num, time_sec):
        round_tick = int(self.round_starts.iloc[round_num - 1]["tick"])
        return round_tick + int(time_sec * self.tickrate)

    @staticmethod
    def _format_time(sec):
        m, s = divmod(int(sec), 60)
        return f"{m}:{s:02d}"

    def format_for_llm(self, state):
        """把状态格式化为 LLM 可读文本."""
        if "error" in state:
            return f"[错误] {state['error']}"

        lines = [
            f"=== 时刻快照: {state['map']} 第{state['round']}回合 {state['time_display']} ===",
            "",
        ]

        for team_name, alive, dead in [
            ("T (恐怖分子)", state["t_alive"], state["t_dead"]),
            ("CT (反恐精英)", state["ct_alive"], state["ct_dead"]),
        ]:
            lines.append(f"[ {team_name} ] 存活 {len(alive)} / 阵亡 {len(dead)}")
            for p in alive:
                lines.append(
                    f"  {p['name']:<20} HP:{p['health']:>3} 甲:{p['armor']:>3}  "
                    f"装备:${p['equip_value']:<4}  {p['weapon']:<18}  "
                    f"({p['position']['x']:.0f}, {p['position']['y']:.0f})"
                )
            for p in dead:
                lines.append(f"  {p['name']:<20} [阵亡]")
            lines.append("")

        return "\n".join(lines)


def quick_test():
    demo_dir = Path("D:/SteamLibrary/steamapps/common/Counter-Strike Global Offensive/game/csgo/replays")
    demos = list(demo_dir.glob("*.dem"))
    if not demos:
        print("未找到 Demo 文件")
        return

    snap = DemoSnapshot(str(demos[0]))
    print(f"地图: {snap.map_name} | 回合数: {len(snap.round_starts)}")
    print()

    # 提取第 3 回合开始后 30 秒
    state = snap.get_tick_state(3, 30)
    print(snap.format_for_llm(state))


if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 3:
        snap = DemoSnapshot(sys.argv[1])
        state = snap.get_tick_state(int(sys.argv[2]), float(sys.argv[3]))
        print(snap.format_for_llm(state))
    else:
        quick_test()

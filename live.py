"""
CS2 实时对局监控 — Game State Integration
========================================
启动一个本地 HTTP 服务，接收 CS2 推送的实时对局数据。

用法:
    from live import CS2LiveMonitor
    
    monitor = CS2LiveMonitor()
    monitor.start()        # 启动 HTTP 服务（默认端口 3000）
    monitor.get_status()   # 获取最新对局数据
"""

import json
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread, Lock
from pathlib import Path


class GSIHandler(BaseHTTPRequestHandler):
    """接收 CS2 GSI 推送的 HTTP Handler."""

    monitor_ref = None  # 类变量，指向 CS2LiveMonitor 实例

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

        if self.monitor_ref:
            try:
                data = json.loads(body.decode("utf-8"))
                self.monitor_ref._update(data)
            except Exception:
                pass

    def log_message(self, format, *args):
        pass  # 不打印日志


class CS2LiveMonitor:
    """CS2 实时对局监控器."""

    def __init__(self, port=3000):
        self.port = port
        self._data = {}
        self._lock = Lock()
        self._server = None
        self._thread = None
        self._running = False

    # ── 数据更新 ──

    def _update(self, data):
        with self._lock:
            self._data = data

    def get_data(self):
        """获取最新的 GSI 数据."""
        with self._lock:
            return dict(self._data)

    # ── 服务生命周期 ──

    def start(self):
        """启动 HTTP 服务（后台线程）."""
        if self._running:
            return

        GSIHandler.monitor_ref = self
        self._server = HTTPServer(("0.0.0.0", self.port), GSIHandler)
        self._running = True
        self._thread = Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()
        print(f"[LIVE] GSI 监听已启动: http://localhost:{self.port}")

    def stop(self):
        """停止服务."""
        if self._server:
            self._server.shutdown()
        self._running = False
        print("[LIVE] GSI 监听已停止")

    def is_connected(self):
        """是否收到过数据."""
        return bool(self._data)

    # ── 数据解析 ──

    def parse(self, data=None):
        """把原始 GSI 数据解析为可读格式."""
        if data is None:
            data = self.get_data()
        if not data:
            return None

        result = {}

        # 玩家信息
        player = data.get("player", {})
        state = player.get("state", {})
        weapons = player.get("weapons", {})

        # 血量 & 护甲
        result["health"] = state.get("health")
        result["armor"] = state.get("armor")
        result["has_helmet"] = state.get("helmet", False)
        result["money"] = state.get("money")
        result["round_kills"] = state.get("round_kills", 0)
        result["round_killhs"] = state.get("round_killhs", 0)

        # 当前武器
        active_weapon_id = player.get("activity", {}).get("weapon")
        current_weapon = None
        for wid, wpn in weapons.items():
            if wid == "0":
                continue  # 跳过无效
            name = wpn.get("name", "").replace("weapon_", "")
            if active_weapon_id and wpn.get("state") == "active":
                current_weapon = name
                result["ammo_clip"] = wpn.get("ammo_clip")
                result["ammo_reserve"] = wpn.get("ammo_reserve")
                break

        if current_weapon:
            result["weapon"] = current_weapon
        elif weapons:
            # 尝试找活跃武器
            for wid, wpn in weapons.items():
                if wid == "0":
                    continue
                if wpn.get("state") == "active":
                    result["weapon"] = wpn.get("name", "").replace("weapon_", "")
                    result["ammo_clip"] = wpn.get("ammo_clip")
                    result["ammo_reserve"] = wpn.get("ammo_reserve")
                    break

        # 位置
        pos = player.get("position", {})
        if pos:
            result["position"] = {
                "x": round(pos.get("x", 0), 1),
                "y": round(pos.get("y", 0), 1),
                "z": round(pos.get("z", 0), 1),
            }

        # 对局信息
        map_info = data.get("map", {})
        if map_info:
            result["map"] = map_info.get("name", "")
            result["phase"] = map_info.get("phase", "")  # live / freezetime / bomb / timeout
            result["round"] = map_info.get("round", 0)
            result["team_t_score"] = map_info.get("team_t_score", 0)
            result["team_ct_score"] = map_info.get("team_ct_score", 0)

        # 队伍信息
        team_map = {"T": 2, "CT": 3}
        for team_name, team_id in team_map.items():
            team_data = data.get("team", {}).get(str(team_id), {})
            if team_data:
                result[f"{team_name}_score"] = team_data.get("score", 0)
                result[f"{team_name}_equip"] = team_data.get("equip_value", 0)
                result[f"{team_name}_timeouts"] = team_data.get("timeouts_remaining", 0)

        # 炸弹
        bomb = data.get("bomb", {})
        if bomb:
            result["bomb_state"] = bomb.get("state", "")  # carried / planted / exploded / defused
            result["bomb_planted"] = bomb.get("state") == "planted"

        return result

    def get_status(self):
        """获取可读的状态信息."""
        parsed = self.parse()
        if not parsed:
            return "未连接，等待对局数据..."

        lines = [f"[LIVE] {parsed.get('map', '?')} — Round {parsed.get('round', 0)}"]
        lines.append(f"       {parsed.get('team_t_score', 0)}:{parsed.get('team_ct_score', 0)}")

        phase = parsed.get("phase", "")
        phase_map = {"live": "对局中", "freezetime": "冻结时间", "bomb": "炸弹已安放", "timeout": "暂停"}
        lines.append(f"       阶段: {phase_map.get(phase, phase)}")

        if parsed.get("health") is not None:
            armor_str = f"+{parsed['armor']}甲" if parsed.get("armor", 0) > 0 else ""
            helmet_str = "+头盔" if parsed.get("has_helmet") else ""
            lines.append(f"       HP: {parsed['health']} {armor_str}{helmet_str}")

        if parsed.get("weapon"):
            ammo = parsed.get("ammo_clip", "?")
            reserve = parsed.get("ammo_reserve", "?")
            lines.append(f"       武器: {parsed['weapon']} ({ammo}/{reserve})")

        if parsed.get("position"):
            p = parsed["position"]
            lines.append(f"       位置: ({p['x']:.0f}, {p['y']:.0f})")

        if parsed.get("money") is not None:
            lines.append(f"       经济: ${parsed['money']}")

        if parsed.get("round_kills", 0) > 0:
            lines.append(f"       本回合击杀: {parsed['round_kills']}")

        return "\n".join(lines)

    def format_for_llm(self, data=None):
        """把当前状态格式化为 LLM 可读的文本."""
        parsed = self.parse(data)
        if not parsed:
            return None

        lines = [f"当前对局: {parsed.get('map', '?')} | 第 {parsed.get('round', 0)} 回合"]
        lines.append(f"比分: T {parsed.get('team_t_score', 0)} - CT {parsed.get('team_ct_score', 0)}")

        phase = parsed.get("phase", "")
        phase_map = {"live": "对局中", "freezetime": "冻结时间", "bomb": "炸弹已安放", "timeout": "暂停"}
        lines.append(f"阶段: {phase_map.get(phase, phase)}")

        if parsed.get("health") is not None:
            lines.append(f"血量: {parsed['health']} | 护甲: {parsed.get('armor', 0)}")
        if parsed.get("weapon"):
            lines.append(f"武器: {parsed['weapon']} ({parsed.get('ammo_clip', '?')}/{parsed.get('ammo_reserve', '?')})")
        if parsed.get("money") is not None:
            lines.append(f"经济: ${parsed['money']}")
        if parsed.get("position"):
            p = parsed["position"]
            lines.append(f"位置坐标: ({p['x']:.0f}, {p['y']:.0f}, {p['z']:.0f})")
        if parsed.get("bomb_state"):
            lines.append(f"炸弹状态: {parsed['bomb_state']}")

        return "\n".join(lines)


# ── 自动生成 GSI 配置 ──

GSI_CFG_CONTENT = r"""
"cs2-live-monitor"
{
    "uri"       "http://localhost:3000"
    "timeout"   "5.0"
    "buffer"    "0.1"
    "throttle"  "0.1"
    "heartbeat" "60.0"
    "data"
    {
        "provider"          "1"
        "map"               "1"
        "round"             "1"
        "player_id"         "1"
        "player_state"      "1"
        "player_weapons"    "1"
        "player_match_stats" "1"
        "player_position"   "1"
        "bomb"              "1"
        "phase_countdowns"  "1"
        "allplayers"        "1"
        "allplayers_id"     "1"
        "allplayers_state"  "1"
        "allplayers_weapons" "1"
        "allplayers_match_stats" "1"
        "allplayers_position" "1"
        "team_state"        "1"
    }
}
"""


def install_gsi_config():
    """自动安装 GSI 配置文件到 CS2 目录."""
    possible_paths = [
        Path("D:/SteamLibrary/steamapps/common/Counter-Strike Global Offensive/game/csgo/cfg"),
        Path("C:/Program Files (x86)/Steam/steamapps/common/Counter-Strike Global Offensive/game/csgo/cfg"),
    ]

    for cfg_dir in possible_paths:
        if cfg_dir.exists():
            cfg_path = cfg_dir / "gamestate_integration_cs2_live.cfg"
            cfg_path.write_text(GSI_CFG_CONTENT, encoding="utf-8")
            print(f"[LIVE] GSI 配置已安装: {cfg_path}")
            return True

    print("[LIVE] 未找到 CS2 cfg 目录，需手动安装 GSI 配置")
    print("      将以下内容保存到: .../csgo/cfg/gamestate_integration_cs2_live.cfg")
    print(GSI_CFG_CONTENT)
    return False


# ── CLI ──

if __name__ == "__main__":
    import sys
    if "--install" in sys.argv:
        install_gsi_config()
    elif "--monitor" in sys.argv:
        quick_test()
    else:
        print("用法:")
        print("  python live.py --install    安装 GSI 配置到 CS2")
        print("  python live.py --monitor    启动实时监控（需先装 GSI）")


def quick_test():
    """启动监控，等待数据，按 Ctrl+C 停止."""
    install_gsi_config()
    monitor = CS2LiveMonitor()
    monitor.start()

    print("\n现在启动 CS2，数据会自动推送过来。")
    print("按 Ctrl+C 停止\n")

    try:
        while True:
            status = monitor.get_status()
            if monitor.is_connected():
                print("\033[2J\033[H")  # 清屏
                print(status)
                print("\n(按 Ctrl+C 停止)")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n已停止")
    finally:
        monitor.stop()

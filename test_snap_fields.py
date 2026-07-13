"""Test snapshot fields."""
from awpy import Demo

d = Demo("D:/SteamLibrary/steamapps/common/Counter-Strike Global Offensive/game/csgo/replays/match730_003793651547057946824_1816938059_401.dem")
td = d.parser.parse_ticks(["X", "Y", "Z", "health", "armor", "team_num", "active_weapon", "current_equip_value"], ticks=[3000])
print("Columns:", td.columns.tolist())
print()
for _, r in td.iterrows():
    w = r.get("active_weapon", "").replace("weapon_", "")
    print(f"{r['name']:20s} HP={r['health']:3d}  armor={r['armor']:3d}  "
          f"team={r['team_num']}  weapon={w:15s}  equip=${r['current_equip_value']}")

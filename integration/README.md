# 🤝 双人集成指南 — 李尚基 × 潘一鸣

你们的两个模块是**互补关系**：

```
李尚基（数据）                   潘一鸣（战术）
   ├─ parser.py：解析 .dem        ├─ 知识库（地图/道具/武器/战术）
   ├─ snapshot.py：时刻快照       ├─ 残局检测算法
   ├─ analysis.py：数据分析       └─ 战术推理引擎
   └─ visualization.py：图表
            │                           │
            └───────────┬───────────────┘
                        ▼
               IntegratedCoach
               （output/__init__.py）
```

---

## 你的模块（李尚基）— 已就绪 ✅

| 文件 | 功能 |
|------|------|
| `parser.py` | 解析 .dem → 击杀/位置/武器数据 |
| `snapshot.py` | 提取指定时刻的全场状态 |
| `analysis.py` | 数据分析 + LLM Prompt |
| `visualization.py` | 图表生成 |
| `report.py` | HTML 报告生成 |
| `memory.py` | 长期记忆 |

## 潘一鸣需要实现的部分 📝

### 1. 知识库（建议结构）

```
knowledge_base/
├── maps/
│   ├── de_dust2.json      地图点位、预瞄点
│   ├── de_mirage.json
│   └── de_inferno.json
├── utility/
│   ├── smoke_lineups.md   烟雾弹路线
│   ├── flash_lineups.md   闪光弹路线
│   └── nade_lineups.md    手雷路线
├── tactics/
│   ├── dust2_a_take.md    打A战术
│   ├── eco_strategy.md    经济局战术
│   └── clutch_guide.md    残局处理
├── weapons/
│   ├── spray_patterns.md  压枪
│   └── damage_data.md     伤害数据
└── __init__.py
```

### 2. 需要实现的接口

```python
# integration/pan_coach.py

class MyTacticalCoach(TacticalCoach):
    
    def find_clutch_rounds(self, demo_analysis) -> list[int]:
        """找出值得分析的残局回合号.
        
        判断依据可用:
        - 回合击杀数 ≤ 3（说明活人少）
        - 1v1 / 1v2 场景
        - 你方经济劣势但赢了
        - 炸弹已安放后的回合
        """
        ...
    
    def analyze(self, round_context) -> dict:
        """分析一个回合，给出战术指导.
        
        round_context 包含:
          - you: 你的位置/血量/武器
          - alive_players: 存活玩家列表
          - map: 地图名
          - bomb_status: 炸弹状态
          
        需要返回:
          - assessment: 形势判断
          - recommended_action: 建议操作
          - position_to_hold: 建议架枪位置
          - utility_to_use: 建议道具
          - reference: 参考战术
        """
        ...
```

### 3. 数据格式说明

你那边给潘一鸣的 **round_context** 例子：

```python
{
    "round": 8,
    "map": "de_dust2",
    "phase": "1v2",
    "time_display": "0:45",
    "you": {
        "name": "基666",
        "health": 45,
        "armor": 50,
        "weapon": "ak-47",
        "position": {"x": 1250, "y": 850}
    },
    "alive_players": [
        {"name": "DONKING", "team": "CT", "health": 75, "weapon": "m4a4"},
        {"name": "encore", "team": "CT", "health": 100, "weapon": "awp"}
    ],
    "dead_players": ["队友A", "队友B"],
    "bomb_status": "planted",
}
```

## 如何合体

### 第一步：潘一鸣完成他的部分

把 `integration/pan_coach.py` 里的 `analyze()` 和 `find_clutch_rounds()` 补全。

### 第二步：测试

```bash
# 李尚基的数据 + 潘一鸣的战术分析
python integration/pan_coach.py
```

输出例子：
```
选手: 基666
数据: 27K / 2.45 K/D

=== 第 4 回合残局分析 ===
你存活，HP=45, 武器=ak-47, 敌人存活 2 人
建议：退到A包箱子后，封拱门烟，只架A大方向

=== 第 8 回合残局分析 ===
...
```

### 第三步：集成到对话模式

等潘一鸣写完，在 `dialog.py` 里加一个 `@tool`：

```python
@tool
def analyze_round(demo_path: str, round_num: int) -> str:
    """分析某一回合的战术."""
    coach = MyTacticalCoach()
    integrated = IntegratedCoach(tactical_coach=coach)
    # ...
```

## 完整目录结构（最终）

```
cs2-agent/
│
├── 李尚基的部分（已完成）
├── main.py
├── parser.py
├── snapshot.py
├── analysis.py
├── visualization.py
├── report.py
├── memory.py
├── tools.py
├── llm.py
├── dialog.py
├── config.py
│
├── 潘一鸣的部分（待实现）
├── integration/
│   ├── __init__.py       ← 集成层 + 接口定义
│   └── pan_coach.py      ← 你的实现模板
├── knowledge_base/       ← 你的数据库
│   ├── maps/
│   ├── utility/
│   ├── tactics/
│   └── weapons/
│
├── requirements.txt
└── README.md
```

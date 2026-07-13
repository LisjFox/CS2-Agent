CS2 AI 教练 🦊

**李尚基 × 潘一鸣 | 清华大学**

一站式 CS2 数据分析 + 战术教练系统。  
解析 Demo → 可视化 HTML 报告 → AI 教练对话 → 残局战术分析 → 职业选手对比 → 知识库语义检索。

---

## 快速开始

```bash
# 1. 装依赖
pip install -r requirements.txt

# 2. 配 Key（编辑 config.py）
#    LLM_API_KEY: *** / DeepSeek / OpenAI 等
#    LLM_API_BASE: https://token-plan.cn-beijing.maas.aliyuncs.com/compatible-mode/v1
#    LLM_MODEL: qwen3.7-plus

# 3. 跑起来
py -3.13 main.py --latest --player "基666"
```

---

## 功能

| 命令 | 说明 |
|------|------|
| `python main.py --latest` | 自动找最近 Demo + 分析 + 进入对话 |
| `python main.py demo.dem` | 分析指定 Demo |
| `python main.py --no-dialog` | 只出报告不对话 |
| `python main.py --history` | 查看所有历史记录 |
| `python main.py --history --player "基666"` | 查看某玩家的历史记录 |
| `python snapshot.py demo.dem 4 75` | 提取第4回合1分15秒的全场快照 |
| `python live.py --install` | 安装 GSI 实时推送配置 |
| `python live.py --monitor` | 启动实时监控 |
| `python test_integration.py` | 运行合体测试（数据→战术分析全流程） |

---

## 完整模块总览

### 数据分析引擎（李尚基）

| 模块 | 功能 |
|------|------|
| `parser.py` | 解析 .dem 文件，提取击杀/位置/武器/选手数据 + 回合分段 |
| `analysis.py` | 特征提取、教练 Prompt 构建、残局检测、回合摘要 |
| `visualization.py` | 击杀热力图、武器统计、选手雷达图、击杀距离散点图 |
| `report.py` | 生成带图表和 AI 点评的 HTML 报告（图片全部 base64 内嵌） |
| `memory.py` | 长期记忆（JSON 文件）+ 短期记忆（对话上下文）+ Demo 文件去重 |
| `pro_data.py` | 20+ 职业选手 × 12 维度数据（HLTV）+ 欧几里得距离对比 |
| `snapshot.py` | 提取指定时刻的全场状态（位置/血量/武器/装备） |
| `live.py` | GSI 实时对局监控（血量/武器/位置） |

### 潘一鸣战术知识库

| 模块 | 内容 |
|------|------|
| `knowledge_base/data/maps.py` | 地图点位数据（Dust2, Mirage, Inferno, Nuke, Ancient, Anubis） |
| `knowledge_base/data/grenades.py` | 投掷物路线数据（烟雾弹/闪光弹/燃烧弹/手雷） |
| `knowledge_base/data/weapons.py` | 武器属性数据（伤害/射速/后座力/穿甲率/价格） |
| `knowledge_base/data/economy.py` | 经济系统数据（胜负奖金/强起/ECO/半起阈值） |
| `knowledge_base/data_loader.py` | 知识库统一加载入口 + 内容切片 |
| `knowledge_base/vector_store.py` | ChromaDB 向量数据库，支持语义检索和按地图/分类过滤 |

### 潘一鸣工具模块

| 模块 | 功能 |
|------|------|
| `tools/map_analyzer.py` | 地图点位查询 + 按场景给战术建议 |
| `tools/weapon_comparer.py` | 武器参数对比 + 预算/阵营推荐 |
| `tools/economy_calculator.py` | 团队经济计算 + 起枪建议 + 经济策略规划 |

### AI 对话与工具系统

| 模块 | 功能 |
|------|------|
| `tools/__init__.py` | 11 个 @tool 函数（7 个你的 + 4 个潘一鸣知识库工具） |
| `dialog.py` | LangChain 对话循环 + @tool 自动路由 |
| `llm.py` | LLM 调用（单次/对话/带工具） |
| `config.py` | 模型配置、颜色常量、武器名映射 |

### 集成层

| 模块 | 功能 |
|------|------|
| `integration/__init__.py` | TacticalCoach / IntegratedCoach 接口定义 |
| `integration/pan_coach.py` | 残局检测 + 知识库查询 + LLM 推理 + 规则兜底（513 行战术引擎） |
| `agent/agent_workflow.py` | Agent 工作流编排 |
| `agent/intent_router.py` | 意图路由 |

### 入口与框架

| 模块 | 功能 |
|------|------|
| `main.py` | CLI 入口，自动找录像是读注册表 + libraryfolders.vdf |
| `test_integration.py` | 全流程集成测试 |

---

## 对话模式支持的 11 个工具

### 你的工具

| 工具 | 说明 |
|------|------|
| `get_player_history` | 查询玩家历史比赛记录 |
| `get_player_trend` | 分析某项指标的趋势（kd / hs_pct 等） |
| `get_all_players` | 查看所有记录过的玩家 |
| `get_training_plan` | 获取每日训练计划（30min/1h/2h 三档） |
| `get_weapon_advice` | 特定武器的训练建议 |
| `compare_with_pro` | 与职业选手对比 / 自动找最相似选手 |
| `get_pro_leaderboard` | 职业选手排行榜（按任意指标排序） |

### 潘一鸣知识库工具

| 工具 | 说明 |
|------|------|
| `query_knowledge` | 语义检索整库（地图/投掷物/武器/经济），支持按地图过滤 |
| `get_map_tactics` | 根据地图 + 阵营 + 场景给战术建议 |
| `get_grenade_routes` | 查特定地图的投掷物路线 |
| `get_eco_advice` | 经济分析 + 起枪建议 |

---

## 工作流程

```
用户打完 CS2 → .dem 文件
  │
  ▼
parser.py 解析数据（击杀/位置/武器/选手 + 回合分段）
  │
  ├─→ visualization.py → report.py → HTML 报告（击杀热力图/武器统计/选手对比/击杀距离）
  │
  ├─→ dialog.py → AI 教练对话
  │      ├─ 调用 @tool 工具（历史/趋势/训练/武器/职业对比）
  │      └─ 调用 @tool 工具（潘一鸣知识库：地图战术/投掷物/经济/语义检索）
  │
  └─→ integration/pan_coach.py
        ├─ 残局检测：从数据中找值得分析的回合
        ├─ 知识库查询：maps / grenades / weapons / economy
        ├─ 向量检索：ChromaDB 语义搜索相似场景
        └─ LLM 推理：形势判断 + 推荐操作 + 道具建议
             │
             ▼
        战术指导输出
```

---

## 配置

编辑 `config.py`:

```python
from langchain_openai import ChatOpenAI

model = ChatOpenAI(
    api_key="***",
    base_url="https://token-plan.cn-beijing.maas.aliyuncs.com/compatible-mode/v1",
    model="qwen3.7-plus",
    temperature=0.7,
)
```

兼容所有 OpenAI 格式的 API。

---

## 职业选手

20+ 选手，12 维度: K/D, HS%, ADR, Rating, KPR, DPR, KAST, Impact, 首杀率, 残局胜率, 多杀率, 道具伤害

包含: s1mple, ZywOo, NiKo, donk, m0NESY, dev1ce, sh1ro, Twistzz, ropz, frozen, EliGE, karrigan, apEX, chopper, somebody, BnTeT 等

---

## 技术栈

| 层 | 技术 |
|----|------|
| Demo 解析 | demoparser2 + awpy |
| LLM 框架 | LangChain (ChatOpenAI) + @tool 装饰器 |
| 大模型 | 通义千问 qwen3.7-plus |
| 知识库 | ChromaDB 向量检索 + 结构化数据（90 条知识条目） |
| 图表 | Matplotlib（深色主题，中文渲染） |
| 记忆 | JSON 文件长期记忆 + 对话上下文短期记忆 |
| 实时 | CS2 Game State Integration |
| 播放器定位 | Steam 注册表 + libraryfolders.vdf 全自动扫描 |
| 报告 | 单文件 HTML（全部资源内嵌，离线可用） |
| 语言 | Python 3.13 |

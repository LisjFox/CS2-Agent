# ============================================================
#  Config — API Key, Model, Theme
#  ============================================================

# --- LangChain 模型配置 ---
import os
from pathlib import Path
from langchain_openai import ChatOpenAI

# 自动加载 .env 文件（如有），优先级：环境变量 > .env > 默认值
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent / ".env")
except ImportError:
    pass

# 兼容两组变量名：.env 里 LLM_API_KEY / config.py 旧版 CS2_LLM_API_KEY
LLM_API_KEY = os.environ.get("LLM_API_KEY") or os.environ.get("CS2_LLM_API_KEY", "")
LLM_API_BASE = os.environ.get("LLM_BASE_URL") or os.environ.get("CS2_LLM_API_BASE", "https://token-plan.cn-beijing.maas.aliyuncs.com/compatible-mode/v1")
LLM_MODEL = os.environ.get("LLM_MODEL_NAME") or os.environ.get("CS2_LLM_MODEL", "qwen3.7-plus")

model = ChatOpenAI(
    api_key=LLM_API_KEY,
    base_url=LLM_API_BASE,
    model=LLM_MODEL,
    temperature=0.7,
    timeout=120,       # 90 秒超时，qwen3.7-plus 对长 prompt 响应较慢
    max_retries=1,     # 允许一次重试
)

# --- Embedding ---
EMBEDDING_API_KEY = LLM_API_KEY
EMBEDDING_MODEL = "text-embedding-v2"

# --- 向量数据库路径（潘一鸣的知识库用） ---
VECTOR_DB_PATH = str(Path.home() / ".cs2_agent_vector_db")

# --- Colors ---
C_T = "#FFD700"
C_CT = "#4A90D9"
C_BG = "#1a1a2e"
C_BG2 = "#16213e"
C_TEXT = "#e0e0e0"
C_ACCENT = "#e94560"
C_GREEN = "#2ECC71"
C_ORANGE = "#E67E22"
C_DEATH = "#e74c3c"
C_KILL = "#2ecc71"

# --- Weapon Names ---
WEAPON_NAMES = {
    "ak-47": "AK-47", "m4a1": "M4A4", "m4a1_silencer": "M4A1-S",
    "m4a4": "M4A4", "galilar": "Galil AR", "famas": "FAMAS",
    "sg556": "SG 553", "aug": "AUG",
    "awp": "AWP", "ssg08": "SSG 08",
    "mp9": "MP9", "mp7": "MP7", "mp5sd": "MP5-SD",
    "mac10": "MAC-10", "bizon": "PP-Bizon", "p90": "P90", "ump45": "UMP-45",
    "deagle": "Desert Eagle", "elite": "Dual Berettas",
    "fiveseven": "Five-SeveN", "glock": "Glock-18",
    "hkp2000": "P2000", "p250": "P250", "tec9": "Tec-9",
    "usp_silencer": "USP-S",
    "nova": "Nova", "xm1014": "XM1014", "mag7": "MAG-7",
    "m249": "M249", "negev": "Negev",
    "hegrenade": "HE", "incgrenade": "燃烧弹", "molotov": "燃烧弹",
    "taser": "Zeus",
    "weapon_knife": "刀", "weapon_knife_butterfly": "蝴蝶刀",
    "weapon_knife_m9_bayonet": "M9刺刀", "weapon_knife_bayonet": "刺刀",
    "weapon_knife_flip": "折叠刀", "weapon_knife_gut": "穿肠刀",
    "weapon_knife_karambit": "爪子刀",
}

WEAPON_CATS = {
    "ak-47": "步枪", "m4a1": "步枪", "m4a1_silencer": "步枪",
    "m4a4": "步枪", "galilar": "步枪", "famas": "步枪",
    "sg556": "步枪", "aug": "步枪",
    "awp": "狙击", "ssg08": "狙击",
    "mp9": "冲锋枪", "mp7": "冲锋枪", "mac10": "冲锋枪",
    "p90": "冲锋枪", "ump45": "冲锋枪", "bizon": "冲锋枪",
    "deagle": "手枪", "glock": "手枪", "usp_silencer": "手枪",
    "hkp2000": "手枪", "p250": "手枪", "elite": "手枪",
    "fiveseven": "手枪", "tec9": "手枪",
    "nova": "霰弹", "xm1014": "霰弹", "mag7": "霰弹",
    "m249": "机枪", "negev": "机枪",
    "hegrenade": "道具", "incgrenade": "道具", "molotov": "道具",
}

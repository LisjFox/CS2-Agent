"""CS2 知识库数据加载器：合并所有数据源并切片"""

from typing import List, Dict
from .data.maps import MAP_KNOWLEDGE
from .data.weapons import WEAPON_KNOWLEDGE
from .data.economy import ECONOMY_KNOWLEDGE
from .data.grenades import GRENADE_KNOWLEDGE


def get_all_knowledge() -> List[Dict]:
    """合并所有知识库数据"""
    return MAP_KNOWLEDGE + WEAPON_KNOWLEDGE + ECONOMY_KNOWLEDGE + GRENADE_KNOWLEDGE


def chunk_knowledge(knowledge_items: List[Dict], chunk_size: int = 500, chunk_overlap: int = 50) -> List[Dict]:
    """将知识条目按内容长度切片，生成多个小块

    切片的目的是让每个 chunk 体积适中，便于向量检索时匹配精准。
    """
    chunks = []
    for item in knowledge_items:
        content = item["content"]
        # 如果内容较短，直接作为一个 chunk
        if len(content) <= chunk_size:
            chunks.append({
                "id": item["id"],
                "text": content,
                "metadata": {
                    "title": item["title"],
                    "category": item.get("category", ""),
                    "map": item.get("map", ""),
                    "type": item.get("type", ""),
                }
            })
        else:
            # 较长的内容按段落拆分后再合并
            paragraphs = content.split("\n")
            current_chunk = ""
            chunk_index = 0
            for para in paragraphs:
                if len(current_chunk) + len(para) > chunk_size and current_chunk:
                    chunks.append({
                        "id": f"{item['id']}_p{chunk_index}",
                        "text": current_chunk.strip(),
                        "metadata": {
                            "title": item["title"],
                            "category": item.get("category", ""),
                            "map": item.get("map", ""),
                            "type": item.get("type", ""),
                        }
                    })
                    current_chunk = para
                    chunk_index += 1
                else:
                    if current_chunk:
                        current_chunk += "\n" + para
                    else:
                        current_chunk = para
            if current_chunk:
                chunks.append({
                    "id": f"{item['id']}_p{chunk_index}",
                    "text": current_chunk.strip(),
                    "metadata": {
                        "title": item["title"],
                        "category": item.get("category", ""),
                        "map": item.get("map", ""),
                        "type": item.get("type", ""),
                    }
                })
    return chunks


def load_knowledge_chunks() -> List[Dict]:
    """加载并切片知识库"""
    all_knowledge = get_all_knowledge()
    return chunk_knowledge(all_knowledge)
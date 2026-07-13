"""Chroma 向量数据库管理"""

import os
from typing import List, Dict, Optional
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

from config import VECTOR_DB_PATH
from .data_loader import load_knowledge_chunks


class VectorStore:
    """CS2 知识库向量数据库管理"""

    def __init__(self, collection_name: str = "cs2_knowledge"):
        self.collection_name = collection_name
        # 使用本地嵌入模型
        self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()
        self.client = chromadb.PersistentClient(
            path=VECTOR_DB_PATH,
            settings=Settings(anonymized_telemetry=False),
        )
        self.collection = self._get_or_create_collection()

    def _get_or_create_collection(self):
        """获取或创建集合"""
        try:
            return self.client.get_collection(self.collection_name, embedding_function=self.embedding_fn)
        except (ValueError, chromadb.errors.NotFoundError):
            return self.client.create_collection(self.collection_name, embedding_function=self.embedding_fn)

    def build_index(self, force_rebuild: bool = False):
        """构建/重建知识库索引"""
        if force_rebuild:
            try:
                self.client.delete_collection(self.collection_name)
            except ValueError:
                pass
            self.collection = self._get_or_create_collection()

        # 检查是否已有数据
        if self.collection.count() > 0:
            return

        chunks = load_knowledge_chunks()
        ids = [c["id"] for c in chunks]
        texts = [c["text"] for c in chunks]
        metadatas = [c["metadata"] for c in chunks]

        # 分批添加，避免单次请求过大
        batch_size = 100
        for i in range(0, len(ids), batch_size):
            self.collection.add(
                ids=ids[i:i + batch_size],
                documents=texts[i:i + batch_size],
                metadatas=metadatas[i:i + batch_size],
            )

    def search(self, query: str, top_k: int = 5, filter_metadata: Optional[Dict] = None) -> List[Dict]:
        """检索知识库

        Args:
            query: 查询文本
            top_k: 返回最相似的前 k 条
            filter_metadata: 过滤条件，如 {"map": "Mirage"}

        Returns:
            检索结果列表
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            where=filter_metadata,
        )

        documents = []
        if results["documents"] and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                documents.append({
                    "text": doc,
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "score": results["distances"][0][i] if results["distances"] else 0,
                })
        return documents

    def search_by_category(self, query: str, category: str, top_k: int = 3) -> List[Dict]:
        """按分类检索"""
        return self.search(query, top_k=top_k, filter_metadata={"category": category})

    def search_by_map(self, query: str, map_name: str, top_k: int = 3) -> List[Dict]:
        """按地图检索"""
        return self.search(query, top_k=top_k, filter_metadata={"map": map_name})


# 全局单例
_store: Optional[VectorStore] = None


def get_vector_store() -> VectorStore:
    """获取全局向量数据库实例"""
    global _store
    if _store is None:
        _store = VectorStore()
    return _store
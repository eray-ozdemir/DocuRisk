"""
DocuRisk - Vektör Veritabanı Modülü
FAISS ile vektör depolama ve semantik arama.
"""
import os
import logging
import pickle
import shutil
from typing import List, Optional
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
from src.embeddings import get_embedding_model
from config import CHROMA_DB_DIR, CHROMA_COLLECTION_NAME, RETRIEVAL_TOP_K

logger = logging.getLogger(__name__)

# FAISS index dosya yolu
FAISS_INDEX_DIR = CHROMA_DB_DIR  # Aynı dizini kullanıyoruz


def get_vector_store() -> Optional[FAISS]:
    """
    Kaydedilmiş FAISS vektör veritabanını yükler.

    Returns:
        FAISS veya None (henüz oluşturulmamışsa)
    """
    index_path = os.path.join(FAISS_INDEX_DIR, "index.faiss")
    if os.path.exists(index_path):
        embedding_model = get_embedding_model()
        vector_store = FAISS.load_local(
            FAISS_INDEX_DIR,
            embedding_model,
            allow_dangerous_deserialization=True,
        )
        return vector_store
    return None


def add_documents(chunks: List[Document]) -> FAISS:
    """
    Doküman parçalarını FAISS vektör veritabanına ekler ve diske kaydeder.

    Args:
        chunks: Parçalanmış doküman listesi

    Returns:
        FAISS: Güncellenmiş vektör veritabanı
    """
    logger.info(f"💾 {len(chunks)} chunk FAISS'e ekleniyor...")
    os.makedirs(FAISS_INDEX_DIR, exist_ok=True)

    embedding_model = get_embedding_model()

    # Mevcut index varsa ona ekle, yoksa yeni oluştur
    existing = get_vector_store()
    if existing is not None:
        existing.add_documents(chunks)
        existing.save_local(FAISS_INDEX_DIR)
        logger.info(f"✅ {len(chunks)} chunk mevcut index'e eklendi!")
        return existing
    else:
        vector_store = FAISS.from_documents(
            documents=chunks,
            embedding=embedding_model,
        )
        vector_store.save_local(FAISS_INDEX_DIR)
        logger.info(f"✅ {len(chunks)} chunk ile yeni index oluşturuldu!")
        return vector_store


def similarity_search(query: str, top_k: int = RETRIEVAL_TOP_K) -> List[Document]:
    """
    Verilen sorguya en benzer doküman parçalarını getirir.

    Args:
        query: Arama sorgusu
        top_k: Döndürülecek sonuç sayısı

    Returns:
        List[Document]: En benzer doküman parçaları
    """
    vector_store = get_vector_store()
    if vector_store is None:
        logger.warning("⚠️ Veritabanı boş — önce doküman yükleyin.")
        return []

    results = vector_store.similarity_search(query, k=top_k)
    logger.info(f"🔍 '{query[:50]}...' için {len(results)} sonuç bulundu")
    return results


def get_retriever(top_k: int = RETRIEVAL_TOP_K):
    """
    LangChain uyumlu retriever döner (RAG zinciri için).

    Args:
        top_k: Döndürülecek sonuç sayısı

    Returns:
        VectorStoreRetriever veya None
    """
    vector_store = get_vector_store()
    if vector_store is None:
        return None
    return vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": top_k},
    )


def clear_database():
    """Vektör veritabanını temizler."""
    if os.path.exists(FAISS_INDEX_DIR):
        shutil.rmtree(FAISS_INDEX_DIR)
        os.makedirs(FAISS_INDEX_DIR, exist_ok=True)
        logger.info("🗑️ Veritabanı temizlendi!")


def get_collection_stats() -> dict:
    """Koleksiyon istatistiklerini döner."""
    try:
        vector_store = get_vector_store()
        if vector_store is not None:
            count = vector_store.index.ntotal
            return {"koleksiyon_adi": "faiss_index", "toplam_vektör": count}
        return {"koleksiyon_adi": "faiss_index", "toplam_vektör": 0}
    except Exception:
        return {"koleksiyon_adi": "faiss_index", "toplam_vektör": 0}

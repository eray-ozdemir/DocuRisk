"""
DocuRisk - Embedding Modülü
HuggingFace multilingual-e5-large ile metin vektörizasyonu.
"""
import logging
from langchain_community.embeddings import HuggingFaceEmbeddings
from config import EMBEDDING_MODEL_NAME, EMBEDDING_DEVICE

logger = logging.getLogger(__name__)

# Singleton pattern - model bir kez yüklenir
_embedding_model = None


def get_embedding_model() -> HuggingFaceEmbeddings:
    """
    Embedding modelini döner. İlk çağrıda modeli indirir ve cache'ler.
    Sonraki çağrılarda cache'ten yükler.
    
    Returns:
        HuggingFaceEmbeddings: Embedding modeli
    """
    global _embedding_model
    
    if _embedding_model is None:
        logger.info(f"🔢 Embedding modeli yükleniyor: {EMBEDDING_MODEL_NAME}")
        logger.info(f"   Cihaz: {EMBEDDING_DEVICE}")
        
        _embedding_model = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL_NAME,
            model_kwargs={"device": EMBEDDING_DEVICE},
            encode_kwargs={
                "normalize_embeddings": True,  # Kosinüs benzerliği için normalize
                "batch_size": 32,
            },
        )
        
        logger.info("✅ Embedding modeli hazır!")
    
    return _embedding_model

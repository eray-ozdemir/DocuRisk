"""
DocuRisk - Metin Parçalama (Chunking) Modülü
Hukuki metinleri anlamlı parçalara böler.
"""
import logging
from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from config import CHUNK_SIZE, CHUNK_OVERLAP, CHUNK_SEPARATORS

logger = logging.getLogger(__name__)


def create_chunks(documents: List[Document]) -> List[Document]:
    """
    Dokümanları hukuki bütünlüğü koruyarak parçalara böler.
    
    Strateji:
    - 1000 karakter chunk boyutu
    - 200 karakter örtüşme (overlap) ile bağlam korunur
    - Hukuki madde sınırlarına göre akıllı bölme
    
    Args:
        documents: Sayfa bazlı doküman listesi
        
    Returns:
        List[Document]: Parçalanmış doküman listesi
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=CHUNK_SEPARATORS,
        length_function=len,
        is_separator_regex=False,
    )
    
    chunks = text_splitter.split_documents(documents)
    
    # Her chunk'a sıra numarası ekle
    for i, chunk in enumerate(chunks):
        chunk.metadata["chunk_id"] = i
        chunk.metadata["chunk_total"] = len(chunks)
    
    logger.info(f"✂️ {len(documents)} sayfa → {len(chunks)} parçaya bölündü")
    return chunks


def get_chunk_stats(chunks: List[Document]) -> dict:
    """
    Chunk'lar hakkında istatistik bilgisi döner.
    
    Returns:
        dict: Toplam chunk, ortalama uzunluk, min/max uzunluk
    """
    lengths = [len(chunk.page_content) for chunk in chunks]
    return {
        "toplam_chunk": len(chunks),
        "ortalama_uzunluk": sum(lengths) // len(lengths) if lengths else 0,
        "min_uzunluk": min(lengths) if lengths else 0,
        "max_uzunluk": max(lengths) if lengths else 0,
        "toplam_karakter": sum(lengths),
    }

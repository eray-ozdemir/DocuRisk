"""
DocuRisk - PDF Yükleme Modülü
PDF dosyalarını okur ve metin olarak çıkarır.
"""
import os
import logging
from typing import List
from langchain_community.document_loaders import PyPDFLoader
from langchain.schema import Document

logger = logging.getLogger(__name__)


def load_pdf(file_path: str) -> List[Document]:
    """
    Tek bir PDF dosyasını yükler ve sayfa bazlı Document listesi döner.
    
    Args:
        file_path: PDF dosyasının tam yolu
        
    Returns:
        List[Document]: Sayfa bazlı doküman listesi
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF dosyası bulunamadı: {file_path}")
    
    logger.info(f"PDF yükleniyor: {file_path}")
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    
    # Her sayfaya metadata ekle
    file_name = os.path.basename(file_path)
    for i, doc in enumerate(documents):
        doc.metadata.update({
            "source": file_name,
            "page": i + 1,
            "total_pages": len(documents),
        })
    
    logger.info(f"✅ {len(documents)} sayfa yüklendi: {file_name}")
    return documents


def load_multiple_pdfs(file_paths: List[str]) -> List[Document]:
    """
    Birden fazla PDF dosyasını yükler.
    
    Args:
        file_paths: PDF dosya yollarının listesi
        
    Returns:
        List[Document]: Tüm dokümanların birleşik listesi
    """
    all_documents = []
    for path in file_paths:
        try:
            docs = load_pdf(path)
            all_documents.extend(docs)
        except Exception as e:
            logger.error(f"❌ PDF yüklenemedi ({path}): {e}")
    
    return all_documents


def save_uploaded_file(uploaded_file, upload_dir: str) -> str:
    """
    Streamlit'ten yüklenen dosyayı diske kaydeder.
    
    Args:
        uploaded_file: Streamlit UploadedFile nesnesi
        upload_dir: Kayıt dizini
        
    Returns:
        str: Kaydedilen dosyanın tam yolu
    """
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, uploaded_file.name)
    
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    logger.info(f"📁 Dosya kaydedildi: {file_path}")
    return file_path

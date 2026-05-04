"""
DocuRisk - Yapılandırma Ayarları
Tüm proje genelinde kullanılan sabitler ve ayarlar.
"""
import os

# ========================
# 📂 Dizin Ayarları
# ========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
CHROMA_DB_DIR = os.path.join(DATA_DIR, "chroma_db")
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")

# ========================
# 🤖 Ollama LLM Ayarları
# ========================
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3"
LLM_TEMPERATURE = 0.2  # Hukuki analiz için düşük sıcaklık (deterministik ama daha uretken)
LLM_TOP_P = 0.9
LLM_NUM_CTX = 4096  # Context window boyutu

# ========================
# 🔢 Embedding Ayarları
# ========================
EMBEDDING_MODEL_NAME = "intfloat/multilingual-e5-large"
EMBEDDING_DEVICE = "cpu"  # GPU varsa "cuda" yapılabilir

# ========================
# ✂️ Chunking Ayarları
# ========================
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
# Hukuki metinler için özel ayırıcılar
CHUNK_SEPARATORS = [
    "\n\nMadde",
    "\n\nMadde ",
    "\n\nMadde:",
    "\n\nMadde :",
    "\n\nARTICLE",
    "\n\n",
    "\n",
    ". ",
    " ",
]

# ========================
# 🔍 Retrieval Ayarları
# ========================
RETRIEVAL_TOP_K = 15  # En yakın 15 chunk getirilir
SIMILARITY_THRESHOLD = 0.3  # Minimum benzerlik eşiği

# ========================
# 📊 Risk Seviyeleri
# ========================
RISK_LEVELS = {
    "yuksek": {"label": "🔴 Yüksek Risk", "color": "#FF4444", "score": 3},
    "orta": {"label": "🟡 Orta Risk", "color": "#FFB800", "score": 2},
    "dusuk": {"label": "🟢 Düşük Risk", "color": "#00C853", "score": 1},
    "bilgi": {"label": "🔵 Bilgilendirme", "color": "#2196F3", "score": 0},
}

# ========================
# 🗃️ ChromaDB Ayarları
# ========================
CHROMA_COLLECTION_NAME = "hukuki_dokumanlar"

# ========================
# 🎨 Streamlit Ayarları
# ========================
APP_TITLE = "⚖️ DocuRisk"
APP_SUBTITLE = "Hukuki Doküman Risk Analizörü"
APP_ICON = "⚖️"
PAGE_LAYOUT = "wide"

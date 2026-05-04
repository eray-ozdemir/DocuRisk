"""
DocuRisk - Ana Streamlit Uygulaması
⚖️ Hukuki Doküman Risk Analizörü
"""
import os
import sys
import time
import logging
import streamlit as st

# Proje kök dizinini Python path'e ekle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import (
    APP_TITLE, APP_SUBTITLE, APP_ICON, PAGE_LAYOUT,
    UPLOADS_DIR, OLLAMA_MODEL,
)
from src.pdf_loader import load_pdf, save_uploaded_file
from src.chunker import create_chunks, get_chunk_stats
from src.vector_store import add_documents, clear_database, get_collection_stats
from src.llm import check_ollama_connection
from src.rag_chain import ask_question

# Logging ayarı
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ========================
# 🎨 Sayfa Yapılandırması
# ========================
st.set_page_config(
    page_title="DocuRisk - Hukuki Analizör",
    page_icon=APP_ICON,
    layout=PAGE_LAYOUT,
    initial_sidebar_state="expanded",
)

# ========================
# 🎨 Özel CSS Stilleri
# ========================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Ana tema */
    .stApp {
        font-family: 'Inter', sans-serif;
    }

    /* Başlık alanı */
    .main-header {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        padding: 2rem 2.5rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        border: 1px solid rgba(255,255,255,0.05);
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    }
    .main-header h1 {
        color: #e94560;
        font-size: 2.2rem;
        font-weight: 700;
        margin: 0;
    }
    .main-header p {
        color: #a8b2d1;
        font-size: 1.1rem;
        margin: 0.3rem 0 0 0;
    }

    /* Durum kartları */
    .status-card {
        background: linear-gradient(145deg, #1a1a2e, #16213e);
        border: 1px solid rgba(233,69,96,0.2);
        border-radius: 12px;
        padding: 1.2rem;
        margin: 0.5rem 0;
        box-shadow: 0 4px 16px rgba(0,0,0,0.2);
    }
    .status-card.success {
        border-color: rgba(0,200,83,0.3);
    }
    .status-card.warning {
        border-color: rgba(255,184,0,0.3);
    }
    .status-card.error {
        border-color: rgba(255,68,68,0.3);
    }

    /* Risk badge */
    .risk-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .risk-high { background: rgba(255,68,68,0.2); color: #ff4444; }
    .risk-medium { background: rgba(255,184,0,0.2); color: #ffb800; }
    .risk-low { background: rgba(0,200,83,0.2); color: #00c853; }

    /* Chat mesajları */
    .chat-user {
        background: linear-gradient(135deg, #0f3460, #16213e);
        border-radius: 16px 16px 4px 16px;
        padding: 1rem 1.3rem;
        margin: 0.5rem 0;
        border: 1px solid rgba(233,69,96,0.15);
    }
    .chat-bot {
        background: linear-gradient(135deg, #1a1a2e, #0f3460);
        border-radius: 16px 16px 16px 4px;
        padding: 1rem 1.3rem;
        margin: 0.5rem 0;
        border: 1px solid rgba(0,200,83,0.15);
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }

    /* Metrik kartları */
    .metric-card {
        background: linear-gradient(145deg, #16213e, #1a1a2e);
        border: 1px solid rgba(255,255,255,0.05);
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
    }
    .metric-card .value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #e94560;
    }
    .metric-card .label {
        font-size: 0.8rem;
        color: #a8b2d1;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Buton stilleri */
    .stButton > button {
        background: linear-gradient(135deg, #e94560, #c23152) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        padding: 0.6rem 1.5rem !important;
        transition: all 0.3s ease !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(233,69,96,0.4) !important;
    }

    /* Dosya yükleyici */
    .stFileUploader {
        border: 2px dashed rgba(233,69,96,0.3) !important;
        border-radius: 12px !important;
    }

    /* Divider */
    .fancy-divider {
        height: 2px;
        background: linear-gradient(90deg, transparent, #e94560, transparent);
        margin: 1.5rem 0;
        border: none;
    }
</style>
""", unsafe_allow_html=True)


# ========================
# 🏠 Ana Başlık
# ========================
st.markdown("""
<div class="main-header">
    <h1>⚖️ DocuRisk</h1>
    <p>Yapay Zeka Destekli Hukuki Doküman Risk Analizörü</p>
</div>
""", unsafe_allow_html=True)


# ========================
# 📊 Session State Başlat
# ========================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "doc_processed" not in st.session_state:
    st.session_state.doc_processed = False
if "doc_name" not in st.session_state:
    st.session_state.doc_name = ""
if "chunk_stats" not in st.session_state:
    st.session_state.chunk_stats = {}


# ========================
# 📂 Sidebar
# ========================
with st.sidebar:
    st.markdown("## 🔧 Sistem Durumu")
    st.markdown('<div class="fancy-divider"></div>', unsafe_allow_html=True)

    # Ollama bağlantı kontrolü
    ollama_status = check_ollama_connection()
    if ollama_status["connected"]:
        if ollama_status["has_model"]:
            st.success(f"✅ Ollama bağlı — `{OLLAMA_MODEL}`")
        else:
            st.warning(f"⚠️ Ollama bağlı ama `{OLLAMA_MODEL}` modeli yok")
            st.code(f"ollama pull {OLLAMA_MODEL}", language="bash")
    else:
        st.error("❌ Ollama bağlantısı yok")
        st.info("Terminalde şu komutları çalıştırın:")
        st.code("ollama serve\nollama pull llama3", language="bash")

    st.markdown('<div class="fancy-divider"></div>', unsafe_allow_html=True)

    # Veritabanı durumu
    st.markdown("## 💾 Veritabanı")
    db_stats = get_collection_stats()
    st.metric("Kayıtlı Vektör", db_stats["toplam_vektör"])

    if st.button("🗑️ Veritabanını Temizle", use_container_width=True):
        clear_database()
        st.session_state.doc_processed = False
        st.session_state.messages = []
        st.rerun()

    st.markdown('<div class="fancy-divider"></div>', unsafe_allow_html=True)

    # Doküman bilgisi
    if st.session_state.doc_processed:
        st.markdown("## 📄 Yüklü Doküman")
        st.info(f"📁 {st.session_state.doc_name}")
        stats = st.session_state.chunk_stats
        col1, col2 = st.columns(2)
        col1.metric("Parça", stats.get("toplam_chunk", 0))
        col2.metric("Karakter", f"{stats.get('toplam_karakter', 0):,}")

    st.markdown('<div class="fancy-divider"></div>', unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align:center;color:#555;font-size:0.75rem;'>"
        "DocuRisk v1.0 — Tüm veriler yerel kalır 🔒</p>",
        unsafe_allow_html=True,
    )


# ========================
# 📄 PDF Yükleme Alanı
# ========================
if not st.session_state.doc_processed:
    st.markdown("### 📤 Sözleşme Yükleyin")
    st.markdown("Analiz etmek istediğiniz PDF dosyasını aşağıya sürükleyin veya seçin.")

    uploaded_file = st.file_uploader(
        "PDF dosyası seçin",
        type=["pdf"],
        accept_multiple_files=False,
        label_visibility="collapsed",
    )

    if uploaded_file is not None:
        if st.button("🚀 Dokümanı İşle ve Analiz Et", use_container_width=True):
            with st.status("📄 Doküman işleniyor...", expanded=True) as status:
                # 1. Kaydet
                st.write("💾 Dosya kaydediliyor...")
                file_path = save_uploaded_file(uploaded_file, UPLOADS_DIR)
                time.sleep(0.3)

                # 2. PDF Yükle
                st.write("📖 PDF okunuyor...")
                documents = load_pdf(file_path)
                st.write(f"   ✅ {len(documents)} sayfa okundu")
                time.sleep(0.3)

                # 3. Chunk
                st.write("✂️ Metin parçalanıyor...")
                chunks = create_chunks(documents)
                chunk_stats = get_chunk_stats(chunks)
                st.write(f"   ✅ {chunk_stats['toplam_chunk']} parçaya bölündü")
                time.sleep(0.3)

                # 4. Vektörize & Kaydet
                st.write("🔢 Vektörizasyon ve depolama yapılıyor...")
                st.write("   ⏳ İlk seferde embedding modeli indirilecek (birkaç dakika sürebilir)")
                add_documents(chunks)
                st.write("   ✅ Vektörler ChromaDB'ye kaydedildi")

                # Session state güncelle
                st.session_state.doc_processed = True
                st.session_state.doc_name = uploaded_file.name
                st.session_state.chunk_stats = chunk_stats

                status.update(label="✅ Doküman başarıyla işlendi!", state="complete")

            st.rerun()

# ========================
# 💬 Sohbet Arayüzü
# ========================
else:
    # Analiz türü seçimi
    st.markdown("### 💬 Dokümanınızı Sorgulayın")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("🔴 Risk Analizi", use_container_width=True):
            st.session_state.analysis_type = "risk"
            auto_q = "Bu sözleşmedeki tüm riskli maddeleri tespit et ve risk seviyelerini belirle."
            st.session_state.auto_question = auto_q
    with col2:
        if st.button("📋 Özet Çıkar", use_container_width=True):
            st.session_state.analysis_type = "summary"
            auto_q = "Bu sözleşmenin genel bir özetini çıkar."
            st.session_state.auto_question = auto_q
    with col3:
        if st.button("📖 Madde Açıkla", use_container_width=True):
            st.session_state.analysis_type = "explain"
    with col4:
        if st.button("🔄 Karşılaştır", use_container_width=True):
            st.session_state.analysis_type = "compare"

    if "analysis_type" not in st.session_state:
        st.session_state.analysis_type = "risk"

    st.markdown('<div class="fancy-divider"></div>', unsafe_allow_html=True)

    # Mesaj geçmişini göster
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Otomatik soru varsa çalıştır
    auto_q = st.session_state.pop("auto_question", None)
    if auto_q:
        st.session_state.messages.append({"role": "user", "content": auto_q})
        with st.chat_message("user"):
            st.markdown(auto_q)
        with st.chat_message("assistant"):
            with st.spinner("🤖 Analiz yapılıyor..."):
                response = ask_question(auto_q, st.session_state.analysis_type)
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()

    # Kullanıcı girdisi
    if prompt := st.chat_input("Sözleşme hakkında sorunuzu yazın..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("🤖 Analiz yapılıyor..."):
                response = ask_question(prompt, st.session_state.analysis_type)
            st.markdown(response)

        st.session_state.messages.append({"role": "assistant", "content": response})

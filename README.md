# 🏛️ DocuRisk — Hukuki Doküman Risk Analizörü

Yapay zeka destekli, **tamamen yerel** çalışan hukuki doküman analiz sistemi.
RAG (Retrieval-Augmented Generation) mimarisi ile sözleşmelerinizi analiz edin.

## 🔒 Gizlilik
Tüm verileriniz bilgisayarınızda kalır. Hiçbir veri dış servislere gönderilmez.

## 🚀 Kurulum

### 1. Python Bağımlılıkları
```bash
pip install -r requirements.txt
```

### 2. Ollama Kurulumu
[Ollama](https://ollama.ai) indirin ve kurun, ardından:
```bash
ollama serve
ollama pull llama3
```

### 3. Uygulamayı Başlatın
```bash
streamlit run app.py
```

## 📐 Mimari
- **LLM**: Ollama (Llama 3)
- **Orkestrasyon**: LangChain
- **Vektör DB**: ChromaDB
- **Embedding**: HuggingFace multilingual-e5-large
- **Arayüz**: Streamlit

## 📂 Proje Yapısı
```
DocuRisk/
├── app.py              # Ana uygulama
├── config.py           # Yapılandırma
├── requirements.txt    # Bağımlılıklar
├── src/
│   ├── pdf_loader.py   # PDF yükleme
│   ├── chunker.py      # Metin parçalama
│   ├── embeddings.py   # Vektörizasyon
│   ├── vector_store.py # ChromaDB
│   ├── llm.py          # Ollama bağlantısı
│   └── rag_chain.py    # RAG pipeline
├── prompts/
│   └── risk_analysis.py # Prompt şablonları
├── data/chroma_db/     # Vektör veritabanı
└── uploads/            # Yüklenen PDFler
```

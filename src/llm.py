"""
DocuRisk - Yerel LLM Modülü
Ollama üzerinden Llama 3 modeline bağlantı.
"""
import logging
from langchain_community.chat_models import ChatOllama
from config import OLLAMA_BASE_URL, OLLAMA_MODEL, LLM_TEMPERATURE, LLM_NUM_CTX

logger = logging.getLogger(__name__)

_llm_instance = None


def get_llm() -> ChatOllama:
    """Ollama LLM bağlantısını döner (Llama 3)."""
    global _llm_instance
    if _llm_instance is None:
        logger.info(f"🤖 LLM bağlantısı kuruluyor: {OLLAMA_MODEL}")
        _llm_instance = ChatOllama(
            model=OLLAMA_MODEL,
            base_url=OLLAMA_BASE_URL,
            temperature=LLM_TEMPERATURE,
            num_ctx=LLM_NUM_CTX,
        )
        logger.info("✅ LLM bağlantısı hazır!")
    return _llm_instance


def check_ollama_connection() -> dict:
    """Ollama sunucusunun çalışıp çalışmadığını kontrol eder."""
    try:
        import requests
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            model_names = [m["name"] for m in models]
            has_model = any(OLLAMA_MODEL in name for name in model_names)
            return {
                "connected": True,
                "has_model": has_model,
                "available_models": model_names,
                "message": f"✅ Ollama bağlı! Model {'bulundu' if has_model else 'bulunamadı'}.",
            }
        return {"connected": False, "has_model": False, "available_models": [], "message": "❌ Ollama hata döndü."}
    except Exception as e:
        return {"connected": False, "has_model": False, "available_models": [], "message": f"❌ Ollama'ya bağlanılamadı: {e}"}

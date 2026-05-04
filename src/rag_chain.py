"""
DocuRisk - RAG Zinciri Modülü
LangChain ile Retrieval-Augmented Generation pipeline.
"""
import logging
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from src.llm import get_llm
from src.vector_store import get_retriever
from prompts.risk_analysis import (
    RISK_ANALYSIS_PROMPT,
    SUMMARY_PROMPT,
    CLAUSE_EXPLAIN_PROMPT,
    COMPARISON_PROMPT,
)
from config import RETRIEVAL_TOP_K

logger = logging.getLogger(__name__)


def _format_docs(docs):
    """Dokümanları tek bir metin olarak birleştirir."""
    return "\n\n---\n\n".join(
        f"[Sayfa {doc.metadata.get('page', '?')}, Parça {doc.metadata.get('chunk_id', '?')}]\n{doc.page_content}"
        for doc in docs
    )


def create_rag_chain(analysis_type: str = "risk"):
    """
    Belirtilen analiz türüne göre RAG zinciri oluşturur.

    Args:
        analysis_type: "risk", "summary", "explain", "compare"

    Returns:
        Runnable chain
    """
    prompt_map = {
        "risk": RISK_ANALYSIS_PROMPT,
        "summary": SUMMARY_PROMPT,
        "explain": CLAUSE_EXPLAIN_PROMPT,
        "compare": COMPARISON_PROMPT,
    }

    template = prompt_map.get(analysis_type, RISK_ANALYSIS_PROMPT)
    prompt = PromptTemplate(
        template=template,
        input_variables=["context", "question"],
    )

    llm = get_llm()
    retriever = get_retriever(top_k=RETRIEVAL_TOP_K)

    chain = (
        {"context": retriever | _format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    logger.info(f"⛓️ RAG zinciri oluşturuldu (tür: {analysis_type})")
    return chain


def ask_question(question: str, analysis_type: str = "risk") -> str:
    """
    Kullanıcı sorusuna RAG tabanlı yanıt üretir.

    Args:
        question: Kullanıcı sorusu
        analysis_type: Analiz türü

    Returns:
        str: LLM yanıtı
    """
    chain = create_rag_chain(analysis_type)
    response = chain.invoke(question)
    logger.info(f"✅ Yanıt üretildi ({len(response)} karakter)")
    return response

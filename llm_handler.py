# llm_handler.py
import streamlit as st
import logging
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from config import get_api_key
from typing import Dict, Any, Optional, Tuple, Union
from langchain_community.vectorstores import FAISS

logger = logging.getLogger(__name__)

@st.cache_resource(show_spinner=False)
def initialize_llm(config: Dict[str, Any]) -> Optional[Union[ChatGroq, ChatOllama]]:
    """Initialize the language model with caching"""
    try:
        if config["provider"] == "Groq":
            if not config["api_key"]:
                st.error("Groq API key is required")
                st.info("[Get Groq API Key](https://console.groq.com/keys)")
                return None

            return ChatGroq(
                api_key=config["api_key"],
                model_name=config["model"],
                temperature=config["temperature"],
                max_tokens=config["max_tokens"]
            )
        else:
            return ChatOllama(
                model=config["model"],
                base_url=config["api_endpoint"],
                temperature=config["temperature"],
                num_predict=config["max_tokens"]
            )
    except Exception as e:
        logger.error(f"LLM initialization error: {str(e)}")
        st.error(f"Failed to initialize model: {str(e)}")
        return None

def generate_insights(llm: Any, vector_store: FAISS, field_name: str) -> str:
    """Generate all marketing insights using RAG"""
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})
    
    # Create prompts for different fields
    field_prompts = {
        "brand_description": "Based on the provided context, write a concise brand description. Extract information about the company's mission, values, and unique selling points.",
        "target_audience": "Based on the provided context, identify and describe the target audience or customer segments for this business. Include demographics, psychographics, and key characteristics.",
        "products_services": "Based on the provided context, list and briefly describe the main products and/or services offered by the business.",
        "marketing_goals": "Based on the provided context, identify the key marketing goals or objectives for this business. If not explicitly stated, suggest reasonable goals based on the business type and information provided.",
        "existing_content": "Based on the provided context, summarize any existing marketing content, campaigns, or channels mentioned in the document.",
        "keywords": "Based on the provided context, generate a list of 10-15 relevant keywords for this business that could be used for marketing purposes. Format as a comma-separated list.",
        "suggested_topics": "Based on the provided context, suggest 5-7 content topics that would be relevant for this business's marketing strategy. Present as a numbered list."
    }

    prompt_template = """
    You are a marketing specialist tasked with analyzing business documents.
        
        {input}
        
        Context:
        {context}
        
        Provide a clear, concise response focusing only on the information requested.
    """
    
    document_chain = create_stuff_documents_chain(
        llm,
        ChatPromptTemplate.from_template(prompt_template),
        document_variable_name="context"
    )
    
    retrieval_chain = create_retrieval_chain(retriever, document_chain)
    
    try:
        # Execute the chain
        result = retrieval_chain.invoke({
            "input": field_prompts[field_name]
        })
        return parse_insights(field_name, result["answer"])
    except Exception as e:
        logger.error(f"Insight generation failed: {str(e)}")
        return ""

def parse_insights(field_name: str, text: str) -> str:
    """
    Parses the LLM-generated text for a single field.

    - Trims unnecessary whitespace.
    - Ensures consistent formatting.
    - Handles lists, keywords, and bullet points correctly.

    :param field_name: The name of the field being processed.
    :param text: The raw LLM response.
    :return: Cleaned and formatted text.
    """
    text = text.strip()  # Remove leading/trailing spaces

    # Special handling for keyword-based fields (convert to comma-separated)
    if field_name.lower() in {"keywords", "suggested_topics"}:
        lines = [line.strip("-• ") for line in text.splitlines() if line.strip()]
        return ", ".join(lines)

    return text  # Return cleaned text for normal fields

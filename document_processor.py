# document_processor.py
import streamlit as st
import tempfile
import logging
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from typing import Dict, Any, Optional, Tuple, Union
from config import MAX_FILE_SIZE_MB, SUPPORTED_FILE_TYPES, EMBEDDING_MODEL, DEFAULT_CHUNK_SIZE, DEFAULT_CHUNK_OVERLAP

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def validate_uploaded_file(file: st.runtime.uploaded_file_manager.UploadedFile) -> bool:
    """Validate uploaded file size and type"""
    if file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
        st.error(f"File size exceeds {MAX_FILE_SIZE_MB}MB limit")
        return False
    
    file_extension = file.name.split('.')[-1].lower()
    if file_extension not in SUPPORTED_FILE_TYPES:
        st.error(f"Unsupported file type: {file_extension}")
        return False
    
    return True

@st.cache_data(show_spinner="Processing document...")
def process_document(_file: bytes, file_name: str) -> Tuple[Optional[FAISS], str]:
    """Process uploaded document and create vector store"""
    try:
        # Read the file content directly from the bytes
        file_extension = file_name.split('.')[-1].lower()

        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_extension}") as temp_file:
            temp_file.write(_file)
            temp_path = temp_file.name  # Get the file path
        
        if file_extension == 'pdf':
            loader = PyPDFLoader(temp_path)
        elif file_extension in ['docx', 'doc']:
            loader = Docx2txtLoader(temp_path)
        elif file_extension in ['txt', 'md']:
            loader = TextLoader(temp_path)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
            
        documents = loader.load()
        doc_content = " ".join([doc.page_content for doc in documents])

        # Text splitting
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=DEFAULT_CHUNK_SIZE,
            chunk_overlap=DEFAULT_CHUNK_OVERLAP
        )
        splits = text_splitter.split_documents(documents)

        # Create embeddings
        embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        vector_store = FAISS.from_documents(splits, embeddings)

        return vector_store, doc_content

    except Exception as e:
        logger.error(f"Document processing failed: {str(e)}")
        st.error(f"Document processing error: {str(e)}")
        return None, ""

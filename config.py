import os
from dotenv import load_dotenv

load_dotenv()

# Constants
MAX_FILE_SIZE_MB = 200
SUPPORTED_FILE_TYPES = ["pdf", "docx", "txt", "md"]
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
DEFAULT_CHUNK_SIZE = 1000
DEFAULT_CHUNK_OVERLAP = 100

class Config:
    MARKETING_TASKS = [
        "Marketing Strategy",
        "Campaign Strategy",
        "Social Media Content Strategy",
        "SEO Optimization Strategy",
        "Post Composer"
    ]
    
    API_KEYS = {
        "GROQ": os.getenv("GROQ_API_KEY", ""),
        "OPENAI": os.getenv("OPENAI_API_KEY", ""),
        "PANDASAI": os.getenv("PANDAS_API_KEY", "")
    }

def get_api_key(provider: str) -> str:
    config = Config()
    return config.API_KEYS.get(provider.upper(), "")

class CrawlConfig:
    DEFAULT_PARAMS = {
        "timeout": 30000,
        "max_retries": 3,
        "rate_limit": 5,  # requests per second
        "user_agents": [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15"
        ],
        "proxy_pool": [
            os.getenv("CRAWL_PROXY_1"),
            os.getenv("CRAWL_PROXY_2")
        ]
    }

# web_scraper.py
import asyncio
import logging
import json
from typing import Optional, Dict, Any
from lxml import html
try:
    from crawl4ai import AsyncWebCrawler
except ImportError:
    logging.error("Missing crawl4ai package. Install with: pip install crawl4ai")
    raise
from llm_handler import initialize_llm
from config import get_api_key

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def scrape_website(url: str, llm: Any, options: Optional[Dict[str, Any]] = None) -> Optional[Any]:
    """Scrape a website using crawl4ai and process the content"""
    try:
        # Default options if none provided
        if options is None:
            options = {
                "include_raw_html": True,
                "include_screenshot": False,
                "include_links": False,
                "include_images": False,
                "extraction_strategy": "markdown",
                "browser_options": {
                    "wait_until": "networkidle2",
                    "timeout": 30000,  # 30 seconds in milliseconds
                    "exec_js": True,
                    "stealth_mode": True,
                    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                }
            }
            
            # Validate URL format
            if not url.startswith(('http://', 'https://')):
                raise ValueError(f"Invalid URL format: {url}")

        # Run the crawler
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(url=url, **options)
            
            # Process the scraped content into the vector store
            if result.markdown:
            # Use the LLM from session state
                if not llm:
                    raise ValueError("No LLM configured - check sidebar settings")
                
                # Create extraction prompt
                prompt = f"""Analyze this real estate listing page and extract properties:
                {result.markdown}
                
                Extract structured JSON data with:
                - title (string)
                - price (numeric)
                - location (string)
                - type (string: 'Sale' or 'Rental')
                - description (string)
                - image_url (string)
                """
                
                # Get LLM response using the proper interface
                try:
                    if isinstance(llm, dict):  # Handle config dict from legacy code
                        llm_instance = initialize_llm(llm)
                        response = llm_instance.generate(prompt)
                    else:  # Assume initialized LLM instance
                        response = llm.generate(prompt)
                    
                    # Safely parse LLM response
                    if response and response.text:
                        properties = json.loads(response.text)
                    else:
                        properties = []
                        logger.warning("LLM returned empty response")
                        
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse LLM response: {e}")
                    properties = []
                except Exception as e:
                    logger.error(f"LLM processing failed: {e}")
                    raise

                # Convert to vector store format
                vector_store = {
                    "properties": properties,
                    "raw_html": result.html,
                    "markdown": result.markdown
                }
                return vector_store
                
        return None
        
    except Exception as e:
        logger.error(f"Web scraping failed: {str(e)}")
        raise e

def sync_scrape_website(url: str, llm: Any, options: Optional[Dict[str, Any]] = None) -> Optional[Any]:
    """Synchronous wrapper for scrape_website
    Note: Do not call this from async contexts - use scrape_website directly instead
    """
    try:
        return asyncio.run(scrape_website(url, llm, options))
    except Exception as e:
        logger.error(f"Synchronous scraping failed: {str(e)}")
        return None

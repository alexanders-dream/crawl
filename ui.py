# ui.py
import streamlit as st
import re
from config import Config, get_api_key
from utils import fetch_models
from typing import Dict, Any, Optional, Tuple, Union

# Initialize session state
def initialize_session_state():
    """Initialize Streamlit session state variables"""
    if "initialized" not in st.session_state:
        st.session_state.update({
            "initialized": True,
            "vector_store": None,
            "llm": None,
            "doc_content": "",
            "brand_description": "",
            "target_audience": "",
            "products_services": "",
            "marketing_goals": "",
            "existing_content": "",
            "keywords": "",
            "suggested_topics": "",
            "error_message": "",
            "processing_done": False,
            "task": "Marketing Strategy"  # Initialize task
        })


def create_sidebar() -> Dict[str, Any]:
    """Create the sidebar UI components"""
    default_endpoint = {
                "GROQ": "https://api.groq.com/openai/v1",
                "OPENAI": "https://api.openai.com/v1",
                "OLLAMA": "http://localhost:11434"
            }

    model = None

    # Web scraping section
    with st.sidebar.expander("🌐 Web Scraping", expanded=True):
        st.text_input("URL to Scrape", key="scrape_url")
        scrape_options = {
            "include_raw_html": st.checkbox("Include HTML", False),
            "include_links": st.checkbox("Include Links", False),
            "include_images": st.checkbox("Include Images", False),
            "extraction_strategy": st.selectbox(
                "Extraction Strategy",
                ["markdown", "llm-extraction"],
                index=0
            )
        }
        if st.button("Scrape Website", key="scrape_button"):
            if st.session_state.scrape_url:
                try:
                    with st.spinner("Scraping website..."):
                        from web_scraper import sync_scrape_website
                        vector_store = sync_scrape_website(
                            st.session_state.scrape_url,
                            scrape_options
                        )
                        if vector_store:
                            st.session_state.vector_store = vector_store
                            st.success("Successfully scraped and stored content!")
                        else:
                            st.error("Failed to scrape website content")
                except Exception as e:
                    st.error(f"Scraping failed: {str(e)}")
            else:
                st.warning("Please enter a URL to scrape")

    with st.sidebar:
        with st.expander("Unlock Extra Features", expanded=False):

            st.markdown(
                                """
                                <div style="margin-left: 0px; margin-top: 20px;">
                                    <a href="https://calendly.com/alexanderoguso/30min" target="_blank">
                                        <div style="background-color: #33353d; padding: 15px 30px; border-radius: 8px; text-align: center; width: 250px; height: 54px; display: flex; align-items: center; justify-content: center; transition: all 0.3s ease;">
                                            <span style="color: white; font-weight: 600; font-size: 16px;">📞 Need more? Book a call</span>
                                        </div>
                                    </a>
                                    <p style="color: #ffffff; font-weight: 600; margin-top: 5px; text-align: center;">Let's chat</p>
                                </div>
                                """, unsafe_allow_html=True
                                )
            
            st.markdown(
                                """<div style="text-align: center; margin-top: 20px;">
                                    <a href="https://buymeacoffee.com/oguso">
                                        <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="width: 150px; height: auto;">
                                    </a>
                                    <p style="color: #ffffff; margin-top: 5px;">Support my work!</p>
                                </div>
                                """, unsafe_allow_html=True
                                )

        st.header("🎯 Marketing Task")
        task = st.selectbox(
            "Select Task", 
            options=Config.MARKETING_TASKS,
            index=0
        )

        st.session_state.task = task

        st.title("⚙️ AI Configuration")
        
        provider = st.selectbox(
            "AI Provider", 
            options=["Groq", "Ollama"],
            key="provider_select",
            help="Select your preferred AI service provider"
        )
        
        with st.expander("Provider Settings", expanded=True):
         
            # API Configuration
            if provider == "Groq":
                default_endpoint = "https://api.groq.com/openai/v1"
            else:  # Ollama
                default_endpoint = "http://localhost:11434"


            endpoint = st.text_input(
                "API Endpoint",
                value=default_endpoint,
                key="endpoint_input"
            )
            st.session_state.endpoint = endpoint

            api_key = None
            

            if provider != "Ollama":
                api_key = st.text_input(
                    f"{provider} API Key",
                    type="password",
                    value=get_api_key(provider),
                    help=f"Get your API key from {provider}'s dashboard"
                )
                st.session_state.api_key = api_key
                st.sidebar.markdown("[Get Groq API Key](https://console.groq.com/keys)")
            else:
                st.session_state.api_key = None
                
                st.sidebar.markdown("[Download Ollama](https://ollama.com/)")
                
                           

            # Model selection with caching
        if provider == "Ollama" or st.session_state.get("api_key"):
            with st.spinner("Loading models..."):
                models = fetch_models(
                    provider,
                    st.session_state.get("endpoint"),
                    st.session_state.get("api_key")
                )
               
            model = st.selectbox(
                "Select AI Model",
                models,
                key="model_select",
                help="Select the model version to use"
            )
            st.session_state.model = model
        
        with st.expander("Advanced Settings", expanded=False):
            temperature = st.slider(
                "Temperature", 0.0, 1.0, 0.3,
                help="high temp = high creativity"
            )
            max_tokens = st.number_input(
                "Max Tokens", 
                min_value=512, 
                max_value=8192, 
                value=4096
            )
                        
        
        
    return {
        "provider": provider,
        "model": model,
        "api_key": api_key,
        "api_endpoint": endpoint,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "task": task,
    }

def create_marketing_form() -> Dict[str, str]:
    """Create and handle the main marketing input form"""
    with st.form("marketing_form"):
        st.header("Business Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Brand Identity")
            brand = st.text_area(
                "Description",
                key="brand_description_input",
                value=st.session_state.get("brand_description", ""),
                height=150
            )
            
            st.subheader("Target Audience")
            audience = st.text_area(
                "Target Audience",
                key="target_audience_input",
                value=st.session_state.get("target_audience", ""),
                height=150
            )

            st.subheader("Existing Content")
            existing_content = st.text_area(
                "Existing Content",
                key="existing_content_input",
                value=st.session_state.get("existing_content", ""),
                height=150
            )

                    
        with col2:
            st.subheader("Products/Services")
            products = st.text_area(
                "Products/Services",
                key="products_services_input",
                value=st.session_state.get("products_services", ""),
                height=150
            )
            
            st.subheader("Marketing Goals")
            goals = st.text_area(
                "Marketing Goals",
                key="marketing_goals_input",
                value=st.session_state.get("marketing_goals", ""),
                height=150
            )

            st.subheader("SEO Content Strategy")
            keywords = st.text_area(
                "Keywords",
                key="keywords_input",
                value=st.session_state.get("keywords", ""),
                height=150
            )

        

        st.subheader("Media Communication: Post Composer")
        # Convert suggested_topics to a list of options
        suggested_topics = st.session_state.get("suggested_topics", "")
        topics_list = re.split(r'\d+\.\s*', suggested_topics.strip())

        topics_list = [topic.strip() for topic in topics_list if topic.strip()] if suggested_topics else []
        
        selected_topic = st.selectbox(
            "Suggested Topics",
            key="suggested_topics_input",
            options=["Select a topic"] + topics_list,
            help="Select a suggested topic for your content"
        )
        
        post_type = st.selectbox(
                "Post Type",
                options=["Instagram", "LinkedIn", "Twitter", "Blog", "Podcast", "Media Brief"],
                key="post_type_input",
                help="Select the type of post"
            )
        
        tone = st.selectbox(
                "Tone of Voice",
                options=["Formal", "Casual", "Professional", "Friendly"],
                key="tone_input",
                help="Select the tone for the generated content"
            )
        
        # Add a submit button
        if st.form_submit_button(f"🚀 Generate {st.session_state.task}"):
            return {
                "brand_description": brand,
                "target_audience": audience,
                "products_services": products,
                "marketing_goals": goals,
                "keywords": keywords,
                "suggested_topics": selected_topic,
                "existing_content": existing_content,
                "tone": tone,
                "post_type": post_type
            }
    
    # Display scraped properties carousel
    if st.session_state.get("vector_store"):
        display_property_carousel(st.session_state.vector_store)
    
    return {}

def display_property_carousel(vector_store):
    """Display scraped properties in a carousel layout"""
    st.markdown("""
        <style>
            .property-card {
                border: 1px solid #ddd;
                border-radius: 10px;
                padding: 15px;
                margin: 10px;
                width: 300px;
                height: 400px;
                overflow: hidden;
                background: white;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
            .carousel-container {
                display: flex;
                overflow-x: auto;
                padding: 10px 0;
                gap: 15px;
            }
            .property-image {
                width: 100%;
                height: 180px;
                object-fit: cover;
                border-radius: 5px;
            }
        </style>
    """, unsafe_allow_html=True)
    
    st.subheader("Scraped Properties")
    with st.container():
        st.markdown('<div class="carousel-container">', unsafe_allow_html=True)
        
        # Display each property - assuming vector_store contains list of properties
        for property in vector_store.get("properties", []):
            col = st.columns(1)[0]
            with col:
                st.markdown(f"""
                    <div class="property-card">
                        <img class="property-image" src="{property.get('image_url', '')}">
                        <h3>{property.get('title', 'Property Title')}</h3>
                        <p>{property.get('description', 'Property description')}</p>
                        <div style="margin-top: auto;">
                            <p>🏠 {property.get('type', 'N/A')}</p>
                            <p>💰 {property.get('price', 'N/A')}</p>
                            <p>📍 {property.get('location', 'N/A')}</p>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

# main.py
import streamlit as st
import logging
from ui import initialize_session_state, create_sidebar, create_marketing_form
from document_processor import validate_uploaded_file, process_document
from llm_handler import initialize_llm, generate_insights
from content_generator import generate_output
from file_utils import convert_to_docx
from config import SUPPORTED_FILE_TYPES

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def main():
    initialize_session_state()
    st.set_page_config(page_title="AI Marketing Assistant", layout="wide")
    
    config = create_sidebar()
    st.session_state.llm = initialize_llm(config)
    
    st.title(f"📋 {config['task']} AI Generator")
    
    uploaded_file = st.file_uploader(
        "Upload business document (PDF, DOCX, TXT)", 
        type=SUPPORTED_FILE_TYPES,
        help="add documents to help the AI understand you/your business"
    )
    
    if uploaded_file and validate_uploaded_file(uploaded_file):
        # Reset processing flag if a new file is uploaded
        if ("last_uploaded_file" not in st.session_state or 
            st.session_state.last_uploaded_file != uploaded_file.name):
            st.session_state.processing_done = False
            st.session_state.last_uploaded_file = uploaded_file.name

        # Optionally add a manual reset button for re-running extraction
        if st.button("Extract Data"):
            st.session_state.processing_done = False

        vector_store, content = process_document(
            uploaded_file.getvalue(),
            uploaded_file.name
        )

        st.session_state.vector_store = vector_store
        st.session_state.doc_content = content

        if st.session_state.llm and st.session_state.vector_store and not st.session_state.processing_done:
            # Generate content for the fields
            with st.spinner("Extracting data..."):
                # Always update the value (or conditionally, if you prefer)
                st.session_state.brand_description = generate_insights(
                    st.session_state.llm, st.session_state.vector_store, "brand_description"
                )
                st.session_state.target_audience = generate_insights(
                    st.session_state.llm, st.session_state.vector_store, "target_audience"
                )
                st.session_state.products_services = generate_insights(
                    st.session_state.llm, st.session_state.vector_store, "products_services"
                )
                st.session_state.marketing_goals = generate_insights(
                    st.session_state.llm, st.session_state.vector_store, "marketing_goals"
                )
                st.session_state.existing_content = generate_insights(
                    st.session_state.llm, st.session_state.vector_store, "existing_content"
                )
                st.session_state.keywords = generate_insights(
                    st.session_state.llm, st.session_state.vector_store, "keywords"
                )
                st.session_state.suggested_topics = generate_insights(
                    st.session_state.llm, st.session_state.vector_store, "suggested_topics"
                )

                # Mark processing as done so we don't re-run it on subsequent reruns
                st.session_state.processing_done = True

            st.rerun()  # Force a re-run so the form picks up the new values

    
    # Main form and generation
    form_data = create_marketing_form()
    
    if form_data and st.session_state.llm:
        with st.spinner("Generating content..."):
            result = generate_output(
                st.session_state.llm,
                config["task"],
                form_data
            )
            
            st.subheader("Generated Content")
            st.markdown(result)
            
            # Add download button with format option
            
            docx_file = convert_to_docx(result)
            st.download_button(
                label="Download Result",
                data=docx_file,
                file_name=f"{config['task'].replace(' ', '_')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

if __name__ == "__main__":
    main()
import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.interfaces import (
    index_rfp_responses,
    upload_rfp_interface, 
    direct_query_interface
)
from app.ui_components import display_sidebar_status
from app.processing_utils import initialize_session_state


def main():
    st.set_page_config(
        page_title="RFP Response Generator",
        page_icon="📄",
        layout="wide"
    )
    
    st.title("🔍 RFP Response Generator")
    st.markdown("Upload your RFP document to extract requirements, then generate professional responses using our organizational knowledge base!")
    
    # Initialize session state
    initialize_session_state()
    
    # Create tabs for different functionalities
    tab1, tab2 = st.tabs(["📝 Generate RFP Responses", "📚 Index RFP Responses"])
    
    with tab1:
        generate_rfp_responses()
    
    with tab2:
        index_rfp_responses()
    
    # Sidebar with status and help
    display_sidebar_status()


def generate_rfp_responses():
    """Main RFP response generation functionality"""
    # Create sub-tabs for different input methods
    input_tab1, input_tab2 = st.tabs(["📄 Upload RFP Document", "💬 Direct Query"])
    
    with input_tab1:
        upload_rfp_interface()
    
    with input_tab2:
        direct_query_interface()


if __name__ == "__main__":
    main()
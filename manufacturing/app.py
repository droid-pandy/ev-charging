"""
Agent Test Interface - Simple Streamlit Chat Application
"""
import streamlit as st
import warnings
import logging

warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from session_manager import SessionManager
from chat_handler import ChatHandler

# Sample prompts for Manufacturing agent
SAMPLE_PROMPTS = [
    "What is the current inventory for PCB-ECU-001?",
    "When is the next delivery for SENSOR-TEMP-001?",
    "Show me the BOM for Advanced ECU Module",
    "What is the production schedule for COMP-XYZ-123?"
]

def main():
    """Main application entry point"""
    
    # Page configuration
    st.set_page_config(
        page_title="Manufacturing Agent Test Interface",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Custom CSS for clean, modern interface
    st.markdown(
        """
        <style>
        /* Global styling */
        html, body, [class*="css"] {
            font-family: 'Inter', 'Segoe UI', sans-serif;
            background-color: #FFFFFF;
            color: #262730;
        }
        
        .stMainBlockContainer {
            padding-top: 2em;
            padding-right: 3em;
            padding-left: 3em;
            background-color: #FFFFFF;
        }
        
        /* Hide sidebar */
        section[data-testid="stSidebar"] {
            display: none;
        }
        
        /* Chat container */
        div[data-testid="stChatMessageContainer"] {
            background-color: #F9FAFB;
            border-radius: 8px;
        }
        
        /* Sample prompt buttons */
        .sample-prompt-button {
            margin-bottom: 4px !important;
        }
        
        .sample-prompt-button button {
            font-size: 13px !important;
            padding: 10px 16px !important;
            background-color: #FFFFFF !important;
            color: #262730 !important;
            border: 1px solid #D1D5DB !important;
            border-radius: 8px !important;
            transition: all 0.2s !important;
            margin: 0px !important;
        }
        
        .sample-prompt-button button:hover {
            background-color: #F9FAFB !important;
            border-color: #1E88E5 !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
        }
        
        /* Text area styling */
        textarea {
            border-radius: 8px !important;
            border: 1px solid #D1D5DB !important;
            background-color: #FFFFFF !important;
            color: #262730 !important;
        }
        
        textarea:focus {
            border-color: #1E88E5 !important;
            box-shadow: 0 0 0 2px rgba(30, 136, 229, 0.1) !important;
        }
        
        /* Headers */
        h1 {
            color: #262730 !important;
            font-weight: 600 !important;
        }
        
        h3 {
            color: #4B5563 !important;
            font-weight: 500 !important;
        }
        
        /* Info box */
        .info-box {
            background-color: #EFF6FF;
            border-left: 4px solid #1E88E5;
            padding: 16px;
            border-radius: 8px;
            margin-bottom: 24px;
        }
        
        .info-box p {
            color: #1E3A8A !important;
            margin: 0 !important;
        }
        
        /* Clear chat button */
        .clear-chat-button button {
            background-color: #EF4444 !important;
            color: white !important;
            border: none !important;
            border-radius: 6px !important;
        }
        
        .clear-chat-button button:hover {
            background-color: #DC2626 !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    # Initialize session manager and chat handler
    session_manager = SessionManager()
    chat_handler = ChatHandler(session_manager)
    session_manager.initialize_session_state()
    
    # Header
    st.markdown(
        """
        <h1 style="margin: 0; margin-bottom: 24px;">Manufacturing Agent Test Interface</h1>
        """,
        unsafe_allow_html=True
    )
    
    # Info box
    st.markdown(
        """
        <div class="info-box">
            <p><strong>About Manufacturing Agent:</strong> This agent helps with inventory management, 
            delivery scheduling, bill of materials, and production planning. Try the sample prompts 
            below or ask your own questions.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Chat interface
    chat_handler.setup_chat_interface(sample_prompt=None)
    
    st.markdown("---")
    
    # Display sample prompts in a grid
    cols = st.columns(2)
    for idx, prompt in enumerate(SAMPLE_PROMPTS):
        with cols[idx % 2]:
            st.markdown('<div class="sample-prompt-button">', unsafe_allow_html=True)
            if st.button(f"💡 {prompt}", key=f"sample_{idx}", use_container_width=True):
                # Add the prompt to chat and trigger processing
                st.session_state.messages.append({"role": "user", "content": prompt})
                st.session_state.pending_user_message = prompt
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown(
        """
        <div style="margin-top: 48px; padding-top: 24px; border-top: 1px solid #E5E7EB; text-align: center;">
            <p style="color: #9CA3AF; font-size: 12px;">
                Powered by AWS Bedrock • Amazon Nova Pro • Strands SDK
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()

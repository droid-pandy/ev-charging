"""
Session state management for the Streamlit application
"""
import streamlit as st
import logging
from agent_client import AgentClient

logger = logging.getLogger(__name__)

class SessionManager:
    """Manages session state and agent initialization"""
    
    def __init__(self):
        # Use environment variables or defaults if secrets.toml doesn't exist
        try:
            self.agent_url = st.secrets.get("AGENT_URL", "http://localhost:8080/invocations")
            self.jwt_token = st.secrets.get("JWT_TOKEN", "dummy-token")
        except FileNotFoundError:
            # secrets.toml doesn't exist, use defaults
            self.agent_url = "http://localhost:8080/invocations"
            self.jwt_token = "dummy-token"
    
    def initialize_session_state(self):
        """Initialize session state variables"""
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        if "agent" not in st.session_state:
            st.session_state.agent = self._get_agent()
    
    def _get_agent(self):
        """Initialize agent client"""
        logger.info("Initializing agent client")
        return AgentClient(self.agent_url, self.jwt_token)
    
    def clear_chat_history(self):
        """Clear chat history and reset agent"""
        st.session_state.messages = []
        if "agent" in st.session_state:
            del st.session_state["agent"]
        st.session_state.agent = self._get_agent()
        logger.info("Chat history cleared")

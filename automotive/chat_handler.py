"""
Chat interface and streaming response handling
"""
import streamlit as st
import logging

logger = logging.getLogger(__name__)

class ChatHandler:
    """Handles chat interface and agent communication"""
    
    def __init__(self, session_manager):
        self.session_manager = session_manager

    def _submit_clicked(self):
        """Handle submit button click"""
        st.session_state.messages.append({
            "role": "user", 
            "content": st.session_state.chat_input_field
        })
        st.session_state.pending_user_message = st.session_state.chat_input_field
    
    def _reset_clicked(self):
        """Handle reset button click"""
        self.session_manager.clear_chat_history()
    
    def setup_chat_interface(self, sample_prompt=None):
        """Setup the chat interface"""
        chat_container = st.container(height=450, border=True)
        
        with chat_container:
            for message in st.session_state.messages:
                if message["role"] == "user":
                    with st.chat_message("user", avatar=None):
                        st.write(message['content'])
                else:
                    with st.chat_message("assistant", avatar=None):
                        st.write(message["content"])
        
        # Sample prompt tiles
        st.markdown("""
            <style>
            .small-prompt-button button {
                font-size: 11px !important;
                padding: 8px 12px !important;
            }
            button[kind="primary"], button[kind="secondary"] {
                text-align: left !important;
                justify-content: flex-start !important;
            }
            </style>
        """, unsafe_allow_html=True)
        
        # Display sample prompt if provided
        if sample_prompt:
            st.markdown("<p style='margin-bottom: 5px; margin-top: 5px;'><strong>Try this prompt:</strong></p>", unsafe_allow_html=True)
            
            if st.button(f"{sample_prompt['icon']} {sample_prompt['text']}", key="prompt1", use_container_width=True):
                st.session_state.messages.append({
                    "role": "user", 
                    "content": sample_prompt['text']
                })
                st.session_state.pending_user_message = sample_prompt['text']
                st.rerun()
            
            st.markdown("<div style='margin-bottom: -10px;'></div>", unsafe_allow_html=True)
        
        with st.form(key="chat_form", clear_on_submit=True, border=False):
            agent_available = "agent" in st.session_state and st.session_state.agent is not None
            
            default_value = st.session_state.pop('chat_input', '')
            
            input_col, send_col = st.columns([9, 1])
            
            with input_col:
                st.text_area(
                    "Type your message:", 
                    value=default_value, 
                    key="chat_input_field", 
                    label_visibility="collapsed",
                    disabled=not agent_available,
                    placeholder="Type your message..." if agent_available else "Agent not available",
                    height=125,
                    max_chars=2000
                )
            
            with send_col:
                st.markdown("""
                    <style>
                    button[kind="formSubmit"] {
                        display: flex !important;
                        align-items: center !important;
                        justify-content: center !important;
                    }
                    div[data-testid="column"]:has(button[kind="formSubmit"]) {
                        margin-top: -8px !important;
                    }
                    </style>
                """, unsafe_allow_html=True)
                st.form_submit_button("▶", disabled=not agent_available, help="Send", on_click=self._submit_clicked)
                st.form_submit_button("🧹", type="secondary", help="Reset", on_click=self._reset_clicked)
        
        if "pending_user_message" in st.session_state:
            user_message = st.session_state.pending_user_message
            del st.session_state.pending_user_message
            
            agent_stream = st.session_state.agent.stream_async(user_message)
            
            with chat_container:
                with st.chat_message("assistant", avatar=None):
                    response = st.write_stream(self._stream_response(agent_stream))
            
            st.session_state.messages.append({"role": "assistant", "content": response})
    
    def _stream_response(self, agent_stream):
        """Stream agent responses"""
        async def gen():
            async for event in agent_stream:
                if "error" in event:
                    error_message = event["error"]
                    logger.error(f"Error in agent stream: {error_message}")
                    yield f"Error: {error_message}"
                    break
                
                if "data" in event:
                    yield event["data"]
                elif "raw" in event:
                    yield event["raw"]
        
        return gen()

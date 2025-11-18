import os
import sys
import logging
import importlib
import threading
from functools import lru_cache
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from bedrock_agentcore import BedrockAgentCoreApp, RequestContext
from strands import Agent

import agents as agents_module

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEV_MODE = '--dev' in sys.argv

app = BedrockAgentCoreApp(debug=True)

# Initialize agent orchestrator
agent_orchestrator = agents_module.AgentOrchestrator()

def _filter_simple_types(obj):
    """Remove properties that are not simple types (str, int, float, bool, None)"""
    if isinstance(obj, dict):
        return {k: _filter_simple_types(v) for k, v in obj.items() 
                if isinstance(v, (str, int, float, bool, type(None))) or isinstance(v, (dict, list))}
    elif isinstance(obj, list):
        return [_filter_simple_types(item) for item in obj 
                if isinstance(item, (str, int, float, bool, type(None))) or isinstance(item, (dict, list))]
    return obj

@lru_cache(maxsize=8)
def _get_agent(token: str) -> Agent:
    global agent_orchestrator
    try:
        return agent_orchestrator.create_agent(token)
    except Exception as e:
        raise Exception(f"Failed to create agent: {str(e)}")

def reload_agent_factory():
    global agent_orchestrator
    try:
        logger.info("Reloading agents.py ...")
        importlib.reload(agents_module)
        agent_orchestrator = agents_module.AgentOrchestrator()
        _get_agent.cache_clear()
        logger.info("Reload complete. Cache cleared.")
    except Exception as e:
        logger.error(f"Failed to reload agents: {e}")

class DebouncedHandler(FileSystemEventHandler):
    def __init__(self, filepath, debounce_sec=2):
        self.filepath = os.path.abspath(filepath)
        self.debounce_sec = debounce_sec
        self._timer = None
        super().__init__()

    def on_modified(self, event):
        if os.path.abspath(event.src_path) == self.filepath:
            if self._timer:
                self._timer.cancel()
            self._timer = threading.Timer(self.debounce_sec, reload_agent_factory)
            self._timer.start()

def start_watcher():
    filepath = os.path.abspath("agents.py")
    event_handler = DebouncedHandler(filepath)
    observer = Observer()
    observer.schedule(event_handler, path=os.path.dirname(filepath), recursive=False)
    observer.start()
    logger.info(f"Watching {filepath} for changes")

if DEV_MODE:
    start_watcher()

@app.entrypoint
async def invoke_agent(payload, context: RequestContext):
    logger.info(f"Received prompt: {payload.get('prompt', '')}")
    
    session_id = context.session_id
    
    user_message = payload.get("prompt", "")
    if not user_message:
        raise Exception("No prompt found in input")
    
    # Get agent
    agent = _get_agent("dummy-token")
    
    # Stream response
    stream = agent.stream_async(user_message)
    async for event in stream:
        yield _filter_simple_types(event)

if __name__ == "__main__":
    logger.info("Started in " + ("DEV" if DEV_MODE else "PRODUCTION") + " mode")
    app.run()


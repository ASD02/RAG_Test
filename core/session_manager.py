import json
import os
from typing import Optional, Dict, List
from memory.conversation_memory import ConversationMemory
from datetime import datetime

class SessionManager:
    """Manage session serialization and deserialization."""
    
    def __init__(self, session_file: str = "session.json"):
        self.session_file = session_file
        self.memory = ConversationMemory()
    
    def save_session(self, conversations: List[Dict]):
        """Serialize conversation history to file."""
        session_data = {
            "timestamp": datetime.now().isoformat(),
            "conversations": conversations
        }
        
        with open(self.session_file, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)
    
    def load_session(self) -> Optional[List[Dict]]:
        """Deserialize conversation history from file."""
        if not os.path.exists(self.session_file):
            return None
        
        try:
            with open(self.session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
                return session_data.get("conversations", [])
        except Exception:
            return None
    
    def restore_memory(self):
        """Restore conversation memory from saved session."""
        conversations = self.load_session()
        if conversations:
            for conv in conversations:
                self.memory.add_conversation(
                    question=conv.get("question", ""),
                    answer=conv.get("answer", ""),
                    metadata=conv.get("metadata", {})
                )
    
    def get_all_conversations(self) -> List[Dict]:
        """Get all conversations from memory."""
        return self.memory.get_all_history()
    
    def get_memory(self) -> ConversationMemory:
        """Get the memory instance."""
        return self.memory


import chromadb
from datetime import datetime
from typing import List, Dict, Optional

class ConversationMemory:
    """Store and retrieve conversation history using in-memory ChromaDB."""
    
    def __init__(self, collection_name: str = "conversation_memory"):
        self.client = chromadb.Client()
        self.collection = self.client.get_or_create_collection(name=collection_name)
    
    def add_conversation(self, question: str, answer: str, metadata: Optional[Dict] = None):
        """Store a Q&A pair in memory."""
        timestamp = datetime.now().isoformat()
        combined_text = f"Question: {question}\nAnswer: {answer}"
        
        conv_metadata = {
            "timestamp": timestamp,
            "question": question,
            "answer": answer,
            **(metadata or {})
        }
        
        self.collection.add(
            documents=[combined_text],
            metadatas=[conv_metadata],
            ids=[timestamp]
        )
    
    def get_relevant_history(self, query: str, n_results: int = 3) -> List[Dict]:
        """Retrieve semantically similar past conversations."""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            include=["documents", "metadatas", "distances"]
        )
        
        if not results or not results.get('metadatas') or not results['metadatas'][0]:
            return []
        
        relevant_history = []
        for metadata, distance in zip(results['metadatas'][0], results['distances'][0]):
            relevant_history.append({
                "question": metadata.get("question", ""),
                "answer": metadata.get("answer", ""),
                "timestamp": metadata.get("timestamp", ""),
                "distance": distance,
                "metadata": {k: v for k, v in metadata.items() if k not in ["question", "answer", "timestamp"]}
            })
        
        return relevant_history
    
    def get_all_history(self) -> List[Dict]:
        """Get all conversation history sorted by timestamp."""
        all_results = self.collection.get(include=["metadatas"])
        
        if not all_results or not all_results.get('metadatas'):
            return []
        
        conversations = []
        for metadata in all_results['metadatas']:
            conversations.append({
                "question": metadata.get("question", ""),
                "answer": metadata.get("answer", ""),
                "timestamp": metadata.get("timestamp", ""),
                "metadata": {k: v for k, v in metadata.items() if k not in ["question", "answer", "timestamp"]}
            })
        
        conversations.sort(key=lambda x: datetime.fromisoformat(x['timestamp']).timestamp() if x.get('timestamp') else 0)
        return conversations


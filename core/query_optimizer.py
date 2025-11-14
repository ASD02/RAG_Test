from typing import Optional, List, Dict
from prompts.query_optimizer import QUERY_OPTIMIZER_PROMPT

class QueryOptimizer:
    """Optimize search queries using LLM with conversation history."""
    
    def __init__(self, model):
        self.model = model
    
    def _format_history_context(self, relevant_history: Optional[List[Dict]]) -> str:
        """Format conversation history for query optimization prompt."""
        if not relevant_history:
            return ""
        
        history_context = "\n## PREVIOUS CONVERSATION CONTEXT (MANDATORY TO USE)\n"
        history_context += "The current question is a FOLLOW-UP. You MUST use the context below.\n\n"
        for i, conv in enumerate(relevant_history[:2], 1):
            history_context += f"Previous Conversation {i}:\n"
            history_context += f"Question: {conv['question']}\n"
            history_context += f"Answer summary: {conv['answer'][:250]}...\n\n"
        
        return history_context
    
    def optimize(self, user_question: str, relevant_history: Optional[List[Dict]] = None) -> str:
        """Generate optimized search query."""
        history_context = self._format_history_context(relevant_history)
        
        query_prompt = QUERY_OPTIMIZER_PROMPT.format(
            user_question=user_question,
            history_context=history_context
        )
        
        response = self.model.invoke(query_prompt)
        optimized_query = response.content.strip()
        
        if relevant_history and len(optimized_query.split()) <= 2 and len(user_question.split()) <= 4:
            prev_q = relevant_history[0]['question']
            optimized_query = f"{prev_q} {user_question}"
        
        return optimized_query


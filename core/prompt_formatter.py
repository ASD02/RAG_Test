from typing import Optional, List, Dict
from prompts.tutor_prompt import TUTOR_PROMPT_TEMPLATE, HISTORY_CONTEXT_TEMPLATE

class PromptFormatter:
    """Format prompts for the tutor model."""
    
    def _format_history_text(self, relevant_history: Optional[List[Dict]]) -> str:
        """Format conversation history for inclusion in prompt."""
        if not relevant_history:
            return ""
        
        previous_qa = ""
        for i, conv in enumerate(relevant_history, 1):
            previous_qa += f"**Previous Q&A {i}:**\n"
            previous_qa += f"Question: {conv['question']}\n"
            previous_qa += f"Answer: {conv['answer'][:200]}...\n\n"
        
        return HISTORY_CONTEXT_TEMPLATE.format(previous_qa=previous_qa)
    
    def format(self, user_question: str, documents_text: str, relevant_history: Optional[List[Dict]] = None) -> str:
        """Format complete prompt for tutor model."""
        history_text = self._format_history_text(relevant_history)
        
        return TUTOR_PROMPT_TEMPLATE.format(
            user_question=user_question,
            history_text=history_text,
            documents_text=documents_text
        )


import langchain_ollama
from memory.conversation_memory import ConversationMemory
from core.query_optimizer import QueryOptimizer
from core.query_tokenizer import QueryTokenizer
from core.document_processor import DocumentProcessor
from core.prompt_formatter import PromptFormatter
from core.session_manager import SessionManager

model = langchain_ollama.ChatOllama(
    model="gpt-oss:20b",
    num_ctx=32768    
)

session_manager = SessionManager()
memory = session_manager.get_memory()
query_optimizer = QueryOptimizer(model)
tokenizer = QueryTokenizer()
doc_processor = DocumentProcessor(n_results=20, distance_threshold=1.5)
prompt_formatter = PromptFormatter()

def process_query(user_question: str, relevant_history=None):
    """Process a single query through the complete pipeline."""
    optimized_query = query_optimizer.optimize(user_question, relevant_history)
    print(f"\n[Optimized Query]: {optimized_query}")
    
    key_terms, important_terms = tokenizer.tokenize(optimized_query)
    documents_text, results = doc_processor.process_query(optimized_query, important_terms, key_terms)
    
    dynamic_prompt = prompt_formatter.format(user_question, documents_text, relevant_history)
    print("\n" + "=" * 70)
    print("OPTIMIZED PROMPT SENT TO MODEL")
    print("=" * 70)
    print(dynamic_prompt)
    print("=" * 70 + "\n")
    
    response = model.invoke(dynamic_prompt)
    print("-------------------------------- MODEL RESPONSE --------------------------------")
    print(response.content)
    print("-------------------------------- MODEL RESPONSE --------------------------------")
    
    memory.add_conversation(
        question=user_question,
        answer=response.content,
        metadata={"retrieved_docs_count": len(results.get('documents', [{}])[0]) if results else 0}
    )
    
    return response.content

def get_relevant_history(user_question: str):
    """Get relevant conversation history with fallback."""
    relevant_history = memory.get_relevant_history(user_question, n_results=3)
    
    if relevant_history:
        relevant_history = [conv for conv in relevant_history if conv['distance'] < 1.2]
    
    if not relevant_history:
        all_history = memory.get_all_history()
        if all_history:
            relevant_history = all_history[-2:]
    
    return relevant_history

prompt = input("\nEnter your first question: ")
process_query(prompt, relevant_history=None)

while True:
    print("\n" + "=" * 70)
    prompt = input("Enter another question (or 'quit' to exit): ").strip()
    
    if prompt.lower() in ['quit', 'exit', 'q']:
        conversations = session_manager.get_all_conversations()
        session_manager.save_session(conversations)
        break
    
    if not prompt:
        continue
    
    relevant_history = get_relevant_history(prompt)
    process_query(prompt, relevant_history)

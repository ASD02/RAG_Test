from typing import List, Dict, Tuple, Optional
import utils.chroma_test as chroma_test

class DocumentProcessor:
    """Process document retrieval and filtering."""
    
    def __init__(self, n_results: int = 20, distance_threshold: float = 1.5):
        self.n_results = n_results
        self.distance_threshold = distance_threshold
    
    def retrieve_documents(self, query: str) -> Dict:
        """Retrieve documents from ChromaDB."""
        return chroma_test.query_documents(query, n_results=self.n_results, verbose=False)
    
    def filter_documents(self, results: Dict, important_terms: List[str], key_terms: List[str]) -> List[Tuple]:
        """Filter documents by relevance and keyword matching."""
        filtered_documents = []
        
        if not results or 'documents' not in results or not results['documents']:
            return filtered_documents
        
        distances = results.get('distances', [])
        if distances and len(distances) > 0:
            distances = distances[0]
        else:
            distances = [0.0] * len(results['documents'][0])
        
        for doc, metadata, distance in zip(
            results['documents'][0],
            results['metadatas'][0],
            distances
        ):
            doc_lower = doc.lower()
            
            if important_terms:
                contains_important = any(term in doc_lower for term in important_terms)
            else:
                contains_important = any(term in doc_lower for term in key_terms) if key_terms else True
            
            if contains_important and distance < self.distance_threshold:
                filtered_documents.append((doc, metadata, distance))
        
        return filtered_documents
    
    def format_documents(self, filtered_documents: List[Tuple], fallback_results: Optional[Dict] = None) -> str:
        """Format documents into text for prompt."""
        documents_text = ""
        
        if filtered_documents:
            for i, (doc, metadata, distance) in enumerate(filtered_documents, 1):
                documents_text += f"\n--- Document {i} (Source: {metadata.get('source', 'Unknown')}) ---\n"
                documents_text += f"{doc}\n"
        elif fallback_results and 'documents' in fallback_results and fallback_results['documents']:
            for i, (doc, metadata) in enumerate(zip(
                fallback_results['documents'][0],
                fallback_results['metadatas'][0]
            ), 1):
                documents_text += f"\n--- Document {i} (Source: {metadata.get('source', 'Unknown')}) ---\n"
                documents_text += f"{doc}\n"
        
        return documents_text
    
    def process_query(self, query: str, important_terms: List[str], key_terms: List[str]) -> tuple[str, Dict]:
        """Complete document processing pipeline."""
        results = self.retrieve_documents(query)
        filtered_documents = self.filter_documents(results, important_terms, key_terms)
        documents_text = self.format_documents(filtered_documents, results)
        return documents_text, results


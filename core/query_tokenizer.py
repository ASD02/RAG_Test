from typing import List

class QueryTokenizer:
    """Extract key terms from queries for document filtering."""
    
    def extract_key_terms(self, query: str) -> List[str]:
        """Extract 2-word phrases from query."""
        query_lower = query.lower()
        words = query_lower.split()
        key_terms = [f"{words[i]} {words[i+1]}" for i in range(len(words) - 1) if len(f"{words[i]} {words[i+1]}") > 5]
        return key_terms
    
    def extract_important_terms(self, key_terms: List[str]) -> List[str]:
        """Extract important terms prioritizing domain-specific phrases."""
        important_terms = [term for term in key_terms if all(len(word) > 4 for word in term.split())]
        if not important_terms:
            important_terms = [term for term in key_terms if any(len(word) > 6 for word in term.split())]
        if not important_terms:
            important_terms = key_terms
        return important_terms
    
    def tokenize(self, query: str) -> tuple[List[str], List[str]]:
        """Complete tokenization pipeline."""
        key_terms = self.extract_key_terms(query)
        important_terms = self.extract_important_terms(key_terms)
        return key_terms, important_terms


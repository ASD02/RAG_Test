from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import langchain_ollama

documents = [
    "The capital of France is Paris, a major European city.",
    "The Eiffel Tower is a famous landmark in Paris, France.",
    "The Louvre is the world's largest art museum and a historic monument in Paris.",
    "The currency used in France is the Euro."
]

vectorizer = TfidfVectorizer()
doc_embeddings = vectorizer.fit_transform(documents)

print("Document Embeddings:")
print(doc_embeddings)
print("--------------------------------")

user_query = "What is the currency in France?"

query_embedding = vectorizer.transform([user_query])

similarities = cosine_similarity(query_embedding, doc_embeddings).flatten()

most_relevant_doc_index = np.argmax(similarities)

retrieved_context = documents[most_relevant_doc_index]

print(f"User Query: {user_query}")
print(f"Retrieved Context: {retrieved_context}")
print("---")

augmented_prompt = f"""
Please answer the user's question using only the provided context.

Context:
"{retrieved_context}"

User Question:
"{user_query}"

Answer:
"""

model = langchain_ollama.ChatOllama(
    model="gpt-oss:20b",
    num_ctx=32768    
    )

print("Augmented Prompt (sent to LLM):")
print(augmented_prompt)
print("--------------------------------")

response = model.invoke(augmented_prompt)
print("LLM Response:")
print(response.content)
print("--------------------------------")
import langchain_ollama
import chroma_test

model = langchain_ollama.ChatOllama(
    model="gpt-oss:20b",
    num_ctx=16384
    )

prompt = input("Enter a prompt: ")

results = chroma_test.query_documents(prompt, verbose=False)

# Format the results for the prompt
documents_text = ""
if results and 'documents' in results and results['documents']:
    for i, (doc, metadata) in enumerate(zip(
        results['documents'][0],
        results['metadatas'][0]
    ), 1):
        documents_text += f"\n--- Document {i} (Source: {metadata.get('source', 'Unknown')}) ---\n"
        documents_text += f"{doc}\n"

dynamic_prompt = f"""You are a helpful assistant that can answer questions based on the following retrieved documents.

The user's question is: {prompt}

The relevant documents retrieved from the knowledge base are:
{documents_text}

Please provide a comprehensive answer to the user's question based on the information in these documents. If the documents don't contain enough information to answer the question, please say so.
Do not use any other information than the information in the documents. Do not make up any information.
Do not apply any graphical elements or formatting to the answer. Do not use any other formatting than plain text.
Keep your answer short and to the point. Use markdown formatting for bullet points and lists."""

print(dynamic_prompt)
response = model.invoke(dynamic_prompt)
print("-------------------------------- MODEL RESPONSE --------------------------------")
print(response.content)
print("-------------------------------- MODEL RESPONSE --------------------------------")
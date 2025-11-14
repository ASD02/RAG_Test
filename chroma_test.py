import chromadb
import os
import re
from PyPDF2 import PdfReader

def clean_extracted_text(text):
    """
    Basic text normalization - just normalize whitespace.
    """
    if not text:
        return text
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def convert_to_markdown(file_path, filename):
    """
    Convert a file to markdown representation.
    Returns markdown content as string, or None if conversion fails.
    """
    try:
        if filename.lower().endswith('.pdf'):
            reader = PdfReader(file_path)
            text_content = ""
            for page_num, page in enumerate(reader.pages, start=1):
                page_text = page.extract_text()
                if page_text.strip():
                    cleaned_text = clean_extracted_text(page_text)
                    text_content += f"## Page {page_num}\n\n{cleaned_text}\n\n"
            
            markdown_content = f"# {filename}\n\n{text_content}"
            return markdown_content
        else:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
                content = file.read()
                markdown_content = f"# {filename}\n\n{content}"
                return markdown_content
    except Exception as e:
        print(f"Error converting {filename} to markdown: {e}")
        return None

def ingest_markdown(collection, markdown_content, source_filename):
    """
    Ingest markdown content into ChromaDB collection.
    Splits content into chunks and adds them to the collection.
    """
    if not markdown_content:
        return
    
    chunks = [chunk.strip() for chunk in markdown_content.split('\n\n') if chunk.strip()]
    
    for i, chunk in enumerate(chunks):
        if len(chunk) < 10:
            continue
            
        collection.add(
            documents=[chunk],
            metadatas=[{"source": source_filename, "chunk_index": i}],
            ids=[f"{source_filename}_{i}"])
        print(f"Added chunk {i+1} from {source_filename}")

def ingest_documents():
    """Ingest documents from a folder into ChromaDB."""
    chroma_client = chromadb.PersistentClient(path="chroma_db")
    collection = chroma_client.get_or_create_collection(name="test_collection")
    
    folder_input = input("Enter the folder path: ")
    
    if not os.path.exists(folder_input):
        print(f"Error: Folder '{folder_input}' does not exist.")
        return
    
    print(f"Processing files from {folder_input}...")
    file_count = 0
    
    for filename in os.listdir(folder_input):
        file_path = os.path.join(folder_input, filename)

        if os.path.isdir(file_path):
            continue
        
        markdown_content = convert_to_markdown(file_path, filename)
        
        if markdown_content:
            ingest_markdown(collection, markdown_content, filename)
            file_count += 1
    
    print(f"\nIngestion complete! Processed {file_count} files.")

def query_documents(query=None, n_results=10, verbose=True):
    """
    Query the ChromaDB collection.
    
    Args:
        query: The search query string. If None, will prompt for input.
        n_results: Number of results to return (default 10).
        verbose: If True, print results to console (default True).
    
    Returns:
        Dictionary containing query results with 'documents', 'metadatas', 'distances', and 'ids'.
    """
    chroma_client = chromadb.PersistentClient(path="chroma_db")
    collection = chroma_client.get_or_create_collection(name="test_collection")
    
    if query is None:
        query = input("Enter your query: ")
        n_results_input = input("Number of results (default 10): ").strip()
        n_results = int(n_results_input) if n_results_input.isdigit() else 10
    
    if verbose:
        print(f"\nSearching for: {query}")
    
    results = collection.query(
        query_texts=[query],
        n_results=n_results,
        include=["documents", "metadatas", "distances"]
    )
    
    if verbose:
        print(f"\nFound {len(results['ids'][0])} results:\n")
        for i, (doc, metadata, distance) in enumerate(zip(
            results['documents'][0],
            results['metadatas'][0],
            results['distances'][0]
        ), 1):
            print(f"--- Result {i} (Distance: {distance:.4f}) ---")
            print(f"Source: {metadata.get('source', 'Unknown')}")
            print(f"Chunk Index: {metadata.get('chunk_index', 'N/A')}")
            print(f"Content: {doc[:200]}..." if len(doc) > 200 else f"Content: {doc}")
            print()
    
    return results

def main():
    while True:
        print("\n" + "="*50)
        print("ChromaDB RAG System")
        print("="*50)
        print("1. Ingest documents")
        print("2. Query documents")
        print("3. Exit")
        print("="*50)
        
        choice = input("\nSelect an option (1-3): ").strip()
        
        if choice == "1":
            ingest_documents()
        elif choice == "2":
            query_documents()
        elif choice == "3":
            break
        else:
            print("Invalid choice. Please select 1, 2, or 3.")

if __name__ == "__main__":
    main()
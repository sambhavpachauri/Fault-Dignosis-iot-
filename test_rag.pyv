from sentence_transformers import SentenceTransformer
import faiss
import pickle


# Load the vector database
index = faiss.read_index("rag/maintenance.index")

# Load the original documents
with open("rag/documents.pkl", "rb") as file:
    documents = pickle.load(file)

# Load the same embedding model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


print("RAG search system ready!")
print(f"Knowledge chunks available: {len(documents)}")


while True:

    query = input("\nEnter your maintenance question (or type 'exit'): ")

    if query.lower() == "exit":
        break

    # Convert the question into an embedding
    query_embedding = embedding_model.encode(
        [query],
        convert_to_numpy=True
    )

    # Search the vector database
    distances, indices = index.search(query_embedding, k=3)

    print("\n========== RAG RESULTS ==========")

    for rank, index_number in enumerate(indices[0], start=1):

        print(f"\n--- Result {rank} ---")
        print(documents[index_number])

    print("\n=================================")

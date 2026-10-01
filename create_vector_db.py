from sentence_transformers import SentenceTransformer
import faiss
import os
import pickle


# Load maintenance knowledge
with open("knowledge_base/maintenance_knowledge.txt", "r") as file:
    text = file.read()


# Split using the topic separator
raw_sections = text.split("TOPIC:")

documents = []

for section in raw_sections:

    section = section.strip()

    if not section:
        continue

    # Ignore the final END OF KNOWLEDGE BASE section
    if section.startswith("END OF KNOWLEDGE BASE"):
        continue

    # Put TOPIC: back into the document
    document = "TOPIC: " + section

    documents.append(document)


print(f"Knowledge documents found: {len(documents)}")


# Load embedding model
print("Loading embedding model...")

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

print("Embedding model loaded.")


# Convert documents into embeddings
embeddings = embedding_model.encode(
    documents,
    convert_to_numpy=True
)


# Create FAISS index
dimension = embeddings.shape[1]

index = faiss.IndexFlatL2(dimension)

index.add(embeddings)


# Create RAG directory
os.makedirs("rag", exist_ok=True)


# Save vector index
faiss.write_index(
    index,
    "rag/maintenance.index"
)


# Save documents
with open("rag/documents.pkl", "wb") as file:
    pickle.dump(documents, file)


print("\nRAG vector database rebuilt successfully!")
print(f"Documents indexed: {len(documents)}")
print(f"Embedding dimension: {dimension}")

print("\nSaved:")
print("  → rag/maintenance.index")
print("  → rag/documents.pkl")

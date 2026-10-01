import re
from pathlib import Path
import pickle
import faiss
from sentence_transformers import SentenceTransformer
from backend.schemas.models import StructuredRAGTopic

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
INDEX_PATH = PROJECT_ROOT / "rag" / "maintenance.index"
DOCS_PATH = PROJECT_ROOT / "rag" / "documents.pkl"


def parse_rag_document(raw_text: str) -> StructuredRAGTopic:
    """
    Parses a raw maintenance knowledge chunk into structured fields:
    - topic
    - condition
    - possible causes (list)
    - inspection steps (list)
    - recommended actions (list)
    """
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]

    topic = "GENERAL MAINTENANCE"
    for line in lines:
        if line.startswith("TOPIC:"):
            topic = line.replace("TOPIC:", "").strip(" =#-")
            break

    # Extract Condition
    condition = ""
    cond_match = re.search(r"Condition:\s*(.*?)(?=Possible Causes:|$)", raw_text, re.DOTALL | re.IGNORECASE)
    if cond_match:
        condition = " ".join([l.strip() for l in cond_match.group(1).splitlines() if l.strip()])

    # Extract Possible Causes
    possible_causes = []
    causes_match = re.search(r"Possible Causes:\s*(.*?)(?=Inspection Steps:|$)", raw_text, re.DOTALL | re.IGNORECASE)
    if causes_match:
        for line in causes_match.group(1).splitlines():
            line = line.strip().lstrip("-•*").strip()
            if line:
                possible_causes.append(line)

    # Extract Inspection Steps
    inspection_steps = []
    steps_match = re.search(r"Inspection Steps:\s*(.*?)(?=Recommended Actions:|$)", raw_text, re.DOTALL | re.IGNORECASE)
    if steps_match:
        for line in steps_match.group(1).splitlines():
            line = line.strip()
            if line:
                inspection_steps.append(line)

    # Extract Recommended Actions
    recommended_actions = []
    actions_match = re.search(r"Recommended Actions:\s*(.*?)(?=TOPIC:|END OF|$)", raw_text, re.DOTALL | re.IGNORECASE)
    if actions_match:
        for line in actions_match.group(1).splitlines():
            line = line.strip().lstrip("-•*").strip()
            if line and not line.startswith("="):
                recommended_actions.append(line)

    return StructuredRAGTopic(
        topic=topic,
        condition=condition,
        possible_causes=possible_causes,
        inspection_steps=inspection_steps,
        recommended_actions=recommended_actions,
        raw_text=raw_text
    )


class RAGService:
    def __init__(self, index_path: Path = INDEX_PATH, docs_path: Path = DOCS_PATH):
        if not index_path.exists():
            raise FileNotFoundError(f"FAISS index not found at {index_path}")
        if not docs_path.exists():
            raise FileNotFoundError(f"Documents file not found at {docs_path}")

        print("Loading FAISS index and RAG documents...")
        self.index = faiss.read_index(str(index_path))
        with open(docs_path, "rb") as f:
            self.raw_documents = pickle.load(f)

        print("Loading SentenceTransformer model (all-MiniLM-L6-v2)...")
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

        # Parse all valid knowledge documents (skipping Doc 0 banner if present)
        self.parsed_documents = []
        for doc in self.raw_documents:
            parsed = parse_rag_document(doc)
            if parsed.topic and "MACHINE MAINTENANCE KNOWLEDGE BASE" not in parsed.topic:
                self.parsed_documents.append(parsed)

        print(f"RAGService initialized with {len(self.parsed_documents)} structured knowledge topics.")

    def search(self, query: str, k: int = 1) -> list[StructuredRAGTopic]:
        """
        Embeds query and retrieves top-k structured maintenance topics.
        """
        query_embedding = self.embedding_model.encode([query], convert_to_numpy=True)
        distances, indices = self.index.search(query_embedding, k=k)

        results: list[StructuredRAGTopic] = []
        seen_topics = set()

        for idx in indices[0]:
            if idx < 0 or idx >= len(self.raw_documents):
                continue
            parsed = parse_rag_document(self.raw_documents[idx])
            # Ignore banner chunks and duplicates
            if "MACHINE MAINTENANCE KNOWLEDGE BASE" in parsed.topic or parsed.topic in seen_topics:
                continue
            seen_topics.add(parsed.topic)
            results.append(parsed)

        return results

    def get_all_topics(self) -> list[StructuredRAGTopic]:
        return self.parsed_documents


rag_service = RAGService()

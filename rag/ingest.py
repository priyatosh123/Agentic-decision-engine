import os
import chromadb
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.PersistentClient(path="chroma_db")

def load_documents():
    docs_path = "data/docs"
    documents = []
    ids = []
    metadatas = []

    files = sorted(os.listdir(docs_path))

    for i, filename in enumerate(files):
        if not filename.endswith(".txt"):
            continue

        file_path = os.path.join(docs_path, filename)

        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read().strip()

            if not text:
                continue

            documents.append(text)
            ids.append(f"doc_{i}")
            metadatas.append({"source": filename})

    return documents, ids, metadatas


def ingest():
    documents, ids, metadatas = load_documents()

    if not documents:
        return

    try:
        client.delete_collection(name="decision_engine")
    except:
        pass

    collection = client.get_or_create_collection(name="decision_engine")

    embeddings = model.encode(documents).tolist()

    collection.add(
        documents=documents,
        embeddings=embeddings,
        ids=ids,
        metadatas=metadatas
    )


if __name__ == "__main__":
    ingest()
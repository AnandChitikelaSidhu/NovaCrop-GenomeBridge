import hashlib
from typing import Any

from langchain_core.documents import Document
from pinecone import Pinecone, ServerlessSpec


class PineconeVectorStore:
    """Store and search document embeddings in Pinecone."""

    def __init__(
        self,
        api_key: str,
        index_name: str,
        dimension: int = 1536,
        cloud: str = "aws",
        region: str = "us-east-1",
    ) -> None:
        self.index_name = index_name
        self.dimension = dimension
        self.client = Pinecone(api_key=api_key)
        self._ensure_index(cloud=cloud, region=region)
        self.index = self.client.Index(index_name)

    def _ensure_index(self, *, cloud: str, region: str) -> None:
        existing_indexes = {index_info["name"] for index_info in self.client.list_indexes()}
        if self.index_name in existing_indexes:
            return

        self.client.create_index(
            name=self.index_name,
            dimension=self.dimension,
            metric="cosine",
            spec=ServerlessSpec(cloud=cloud, region=region),
        )

    @staticmethod
    def _vector_id(document: Document, chunk_index: int) -> str:
        source = document.metadata.get("source", "unknown")
        digest = hashlib.sha256(
            f"{source}:{chunk_index}:{document.page_content}".encode("utf-8")
        ).hexdigest()
        return digest

    def upsert_documents(
        self,
        documents: list[Document],
        embeddings: list[list[float]],
    ) -> int:
        if len(documents) != len(embeddings):
            raise ValueError("documents and embeddings must have the same length")

        vectors: list[dict[str, Any]] = []
        for chunk_index, (document, embedding) in enumerate(zip(documents, embeddings)):
            vectors.append(
                {
                    "id": self._vector_id(document, chunk_index),
                    "values": embedding,
                    "metadata": {
                        "text": document.page_content[:8000],
                        "source": str(document.metadata.get("source", "")),
                        "file_type": str(document.metadata.get("file_type", "")),
                        "chunk_index": chunk_index,
                    },
                }
            )

        if not vectors:
            return 0

        batch_size = 100
        for start in range(0, len(vectors), batch_size):
            batch = vectors[start : start + batch_size]
            self.index.upsert(vectors=batch)

        return len(vectors)

    def similarity_search(self, query_embedding: list[float], top_k: int = 5) -> list[dict[str, Any]]:
        response = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True,
        )

        matches = []
        for match in response.get("matches", []):
            metadata = match.get("metadata") or {}
            matches.append(
                {
                    "id": match.get("id"),
                    "score": match.get("score"),
                    "text": metadata.get("text", ""),
                    "source": metadata.get("source", ""),
                    "file_type": metadata.get("file_type", ""),
                }
            )

        return matches

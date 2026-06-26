from langchain_openai import OpenAIEmbeddings


class EmbeddingService:
    """Generate embeddings with OpenAI."""

    def __init__(self, api_key: str, model: str = "text-embedding-3-small") -> None:
        self.client = OpenAIEmbeddings(api_key=api_key, model=model)
        self.model = model

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        return self.client.embed_documents(texts)

    def embed_query(self, text: str) -> list[float]:
        return self.client.embed_query(text)

from functools import lru_cache

from langchain_openai import ChatOpenAI

from app.configs.config import Settings, get_settings
from app.services.rag.embeddings.embedding_service import EmbeddingService
from app.services.rag.loaders.loader_factory import DocumentLoaderFactory
from app.services.rag.rag_service import RAGService
from app.services.rag.splitters.text_splitter_service import TextSplitterService
from app.services.rag.vector_db.pinecone_service import PineconeVectorStore


class RAGFactory:
    """Creates a fully configured RAGService."""

    @staticmethod
    def create(settings: Settings | None = None) -> RAGService:
        settings = settings or get_settings()

        return RAGService(
            settings=settings,
            document_loader=DocumentLoaderFactory.create_default(),
            splitter=TextSplitterService(
                chunk_size=settings.chunk_size,
                chunk_overlap=settings.chunk_overlap,
            ),
            embedding_service=EmbeddingService(
                api_key=settings.openai_api_key,
                model=settings.embedding_model,
            ),
            vector_store=PineconeVectorStore(
                api_key=settings.pinecone_api_key,
                index_name=settings.pinecone_index_name,
                dimension=settings.embedding_dimension,
            ),
            llm=ChatOpenAI(
                api_key=settings.openai_api_key,
                model=settings.chat_model,
                temperature=0,
            ),
        )


@lru_cache
def get_rag_service() -> RAGService:
    return RAGFactory.create()

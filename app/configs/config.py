import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    openai_api_key: str
    pinecone_api_key: str
    pinecone_index_name: str
    embedding_model: str = "text-embedding-3-small"
    chat_model: str = "gpt-4o-mini"
    embedding_dimension: int = 1536
    chunk_size: int = 1000
    chunk_overlap: int = 200
    pubmed_mcp_url: str = os.getenv("PUBMED_MCP_URL")


@lru_cache
def get_settings() -> Settings:
    openai_api_key = os.getenv("OPENAI_API_KEY")
    pinecone_api_key = os.getenv("PINECONE_API_KEY")
    pinecone_index_name = os.getenv("PINECONE_INDEX_NAME")

    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY environment variable is missing")
    if not pinecone_api_key:
        raise ValueError("PINECONE_API_KEY environment variable is missing")
    if not pinecone_index_name:
        raise ValueError("PINECONE_INDEX_NAME environment variable is missing")

    return Settings(
        openai_api_key=openai_api_key,
        pinecone_api_key=pinecone_api_key,
        pinecone_index_name=pinecone_index_name,
        pubmed_mcp_url=os.getenv("PUBMED_MCP_URL"),
    )

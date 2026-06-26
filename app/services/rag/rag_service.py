from pathlib import Path

from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from app.configs.config import Settings
from app.services.rag.embeddings.embedding_service import EmbeddingService
from app.services.rag.loaders.loader_factory import DocumentLoaderFactory
from app.services.rag.models import RAGQueryResult, RetrievedChunk
from app.services.rag.splitters.text_splitter_service import TextSplitterService
from app.services.rag.vector_db.pinecone_service import PineconeVectorStore


class RAGService:
    """
    Orchestrates ingestion and question answering.

    Each step is delegated to an independent service:
    - document loader factory
    - splitter
    - embeddings
    - vector store
    """

    def __init__(
        self,
        settings: Settings,
        document_loader: DocumentLoaderFactory,
        splitter: TextSplitterService,
        embedding_service: EmbeddingService,
        vector_store: PineconeVectorStore,
        llm: ChatOpenAI,
    ) -> None:
        self.settings = settings
        self.document_loader = document_loader
        self.splitter = splitter
        self.embedding_service = embedding_service
        self.vector_store = vector_store
        self.llm = llm

    def ingest_file(self, file_path: str | Path) -> int:
        documents = self.document_loader.load(file_path)
        return self._ingest_documents(documents)

    def ingest_directory(self, directory_path: str | Path) -> int:
        directory = Path(directory_path)
        total = 0

        for extension in self.document_loader.supported_extensions():
            for file_path in sorted(directory.glob(f"*{extension}")):
                total += self.ingest_file(file_path)

        return total

    def ingest_data_directories(
        self,
        *directories: str | Path,
    ) -> dict[str, int]:
        return {
            str(directory): self.ingest_directory(directory)
            for directory in directories
        }

    def _ingest_documents(self, documents: list[Document]) -> int:
        chunks = self.splitter.split(documents)
        texts = [chunk.page_content for chunk in chunks]
        embeddings = self.embedding_service.embed_documents(texts)
        return self.vector_store.upsert_documents(chunks, embeddings)

    def query(self, question: str, top_k: int = 5) -> str:
        return self.query_with_evidence(question, top_k=top_k).answer

    def query_with_evidence(self, question: str, top_k: int = 5) -> RAGQueryResult:
        query_embedding = self.embedding_service.embed_query(question)
        matches = self.vector_store.similarity_search(query_embedding, top_k=top_k)

        if not matches:
            return RAGQueryResult(
                answer="I could not find relevant context in the knowledge base.",
                chunks=[],
            )

        chunks = [
            RetrievedChunk(
                source=str(match.get("source") or "unknown"),
                file_type=str(match.get("file_type") or "unknown"),
                excerpt=str(match.get("text") or ""),
                score=match.get("score"),
            )
            for match in matches
        ]

        context_blocks = []
        for chunk in chunks:
            context_blocks.append(
                f"Source ({chunk.file_type}): {chunk.source}\n{chunk.excerpt}"
            )

        context = "\n\n---\n\n".join(context_blocks)

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are GenomeBridge, NovaCrop Research Labs' research assistant. "
                    "You answer questions using only the retrieved excerpts from NovaCrop's "
                    "internal knowledge base (trial reports, genomic analyses, literature reviews, "
                    "and partner correspondence).\n\n"
                    "Interpretation rules:\n"
                    "- This assistant searches NovaCrop's internal knowledge base only. It does not "
                    "access external literature databases or third-party publications.\n"
                    "- Treat pronouns such as \"we\", \"our\", \"us\", and \"NovaCrop\" as referring "
                    "to NovaCrop's internal knowledge base and research output.\n"
                    "- If the question asks about \"other sources\", \"external studies\", \"what others "
                    "have published\", or similar, answer only from NovaCrop's internal excerpts that "
                    "are relevant to the topic. Do not discuss, disclaim, or apologise for the absence "
                    "of external sources. Never state that no external excerpts were provided or that "
                    "information on other publications is lacking.\n"
                    "- Base every claim on the provided context. Cite the source path for each "
                    "material finding (e.g. Source: ...).\n"
                    "- If the context has no relevant internal information at all, give a brief answer "
                    "that nothing in NovaCrop's knowledge base addresses the topic. Do not invent "
                    "studies, markers, dates, or results.\n"
                    "- Prefer precise, scientific language suitable for genomics and agricultural research.",
                ),
                (
                    "human",
                    "Internal knowledge base excerpts:\n{context}\n\n"
                    "Research question:\n{question}\n\n"
                    "Search the excerpts above and answer using only NovaCrop's internal findings. "
                    "Do not mention external databases or the lack of outside sources.",
                ),
            ]
        )

        chain = prompt | self.llm
        response = chain.invoke({"context": context, "question": question})
        return RAGQueryResult(answer=response.content, chunks=chunks)

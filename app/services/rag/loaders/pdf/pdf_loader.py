from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document

from app.services.rag.loaders.base_loader import BaseLoader


class PDFLoaderService(BaseLoader):
    """Load PDF files into LangChain documents."""

    @property
    def supported_extensions(self) -> frozenset[str]:
        return frozenset({".pdf"})

    def __init__(self, loader_cls: type[PyPDFLoader] = PyPDFLoader) -> None:
        self.loader_cls = loader_cls

    def load(self, file_path: str) -> list[Document]:
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"PDF not found: {file_path}")

        if path.suffix.lower() != ".pdf":
            raise ValueError("Only PDF files are supported.")

        documents = self.loader_cls(str(path)).load()

        for document in documents:
            document.metadata["source"] = str(path.resolve())
            document.metadata["file_type"] = "pdf"

        return documents

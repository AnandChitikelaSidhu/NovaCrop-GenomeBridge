from pathlib import Path

from langchain_core.documents import Document

from app.services.rag.loaders.base_loader import BaseLoader


class TXTLoaderService(BaseLoader):
    """Load plain text files into LangChain documents."""

    @property
    def supported_extensions(self) -> frozenset[str]:
        return frozenset({".txt"})

    def load(self, file_path: str) -> list[Document]:
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"Text file not found: {file_path}")

        if path.suffix.lower() != ".txt":
            raise ValueError("Only .txt files are supported.")

        content = path.read_text(encoding="utf-8")

        return [
            Document(
                page_content=content,
                metadata={
                    "source": str(path.resolve()),
                    "file_type": "txt",
                },
            )
        ]

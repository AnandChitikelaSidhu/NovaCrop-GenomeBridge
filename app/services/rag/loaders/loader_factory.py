from collections.abc import Iterable
from pathlib import Path

from langchain_core.documents import Document

from app.services.rag.loaders.base_loader import BaseLoader
from app.services.rag.loaders.pdf.pdf_loader import PDFLoaderService
from app.services.rag.loaders.txt.txt_loader import TXTLoaderService


class DocumentLoaderFactory:
    """Factory that selects the correct loader strategy for a file."""

    def __init__(self, loaders: Iterable[BaseLoader]) -> None:
        self._loaders = list(loaders)

    @classmethod
    def create_default(cls) -> "DocumentLoaderFactory":
        return cls(
            loaders=[
                PDFLoaderService(),
                TXTLoaderService(),
            ]
        )

    def supported_extensions(self) -> frozenset[str]:
        extensions: set[str] = set()
        for loader in self._loaders:
            extensions.update(loader.supported_extensions)
        return frozenset(extensions)

    def get_loader(self, file_path: str | Path) -> BaseLoader:
        for loader in self._loaders:
            if loader.supports(file_path):
                return loader

        path = Path(file_path)
        supported = ", ".join(sorted(self.supported_extensions()))
        raise ValueError(
            f"Unsupported file type '{path.suffix}' for {path.name}. "
            f"Supported extensions: {supported}"
        )

    def load(self, file_path: str | Path) -> list[Document]:
        return self.get_loader(file_path).load(str(file_path))

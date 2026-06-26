from abc import ABC, abstractmethod
from pathlib import Path

from langchain_core.documents import Document


class BaseLoader(ABC):
    """Strategy interface for document loaders."""

    @property
    @abstractmethod
    def supported_extensions(self) -> frozenset[str]:
        raise NotImplementedError

    def supports(self, file_path: str | Path) -> bool:
        return Path(file_path).suffix.lower() in self.supported_extensions

    @abstractmethod
    def load(self, file_path: str) -> list[Document]:
        raise NotImplementedError

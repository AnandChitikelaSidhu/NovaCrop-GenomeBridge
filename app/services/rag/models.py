from dataclasses import dataclass, field


@dataclass(frozen=True)
class RetrievedChunk:
    source: str
    file_type: str
    excerpt: str
    score: float | None = None


@dataclass(frozen=True)
class RAGQueryResult:
    answer: str
    chunks: list[RetrievedChunk] = field(default_factory=list)

    @property
    def has_context(self) -> bool:
        return len(self.chunks) > 0

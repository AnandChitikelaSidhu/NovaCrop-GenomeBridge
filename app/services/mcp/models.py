from dataclasses import dataclass, field


@dataclass(frozen=True)
class PubMedDateRange:
    min_date: str
    max_date: str
    date_type: str = "pdat"


@dataclass(frozen=True)
class PubMedSearchRequest:
    query: str
    max_results: int = 5
    sort: str = "pub_date"
    has_abstract: bool = True
    date_range: PubMedDateRange | None = None


@dataclass(frozen=True)
class PubMedArticle:
    pmid: str
    title: str
    abstract_text: str
    publication_date: str
    pubmed_url: str
    doi: str | None = None
    pmc_url: str | None = None
    authors: list[str] = field(default_factory=list)
    journal: str | None = None


@dataclass(frozen=True)
class PubMedSearchResult:
    query: str
    pmids: list[str]
    articles: list[PubMedArticle]
    total_count: int | None = None

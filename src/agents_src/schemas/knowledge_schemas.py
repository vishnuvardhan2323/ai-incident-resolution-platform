from pydantic import BaseModel


class KnowledgeResult(BaseModel):
    answer: str
    source_files: list[str]
    grounded: bool
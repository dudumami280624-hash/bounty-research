"""Offline, dependency-free access-control lab. Never binds a socket."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Document:
    owner: str
    body: str

DOCS = {"doc-a": Document("alice", "alice private"), "doc-b": Document("bob", "bob private")}

def vulnerable_read(user: str, document_id: str) -> str:
    """Deliberately flawed IDOR example: ignores the caller's identity."""
    return DOCS[document_id].body

def protected_read(user: str, document_id: str) -> str:
    document = DOCS[document_id]
    if document.owner != user:
        raise PermissionError("not authorized")
    return document.body

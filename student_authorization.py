"""Fail-closed execution authorization for the AI child's security research."""
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class Scope:
    kind: str
    root: str
    approved: bool = False

def authorize(scope: Scope, target: str, operation: str) -> bool:
    """Only approved local training fixture operations can execute automatically."""
    if operation not in {"read", "analyze", "compile", "test", "local-poc"}:
        return False
    if scope.kind != "local-training" or not scope.approved:
        return False
    root = Path(scope.root).resolve()
    destination = Path(target).resolve()
    if not destination.is_relative_to(root):
        return False
    return True

def require_authorization(scope: Scope, target: str, operation: str) -> None:
    if not authorize(scope, target, operation):
        raise PermissionError(f"Unauthorized operation: {operation}")

from lark import Lark, Transformer, Token
from dataclasses import dataclass, field

@dataclass
class DiffStats:
    wire_added: int = 0
    wire_removed: int = 0
    track_added: int = 0
    track_removed: int = 0

def count_changes(diff_path: str) -> DiffStats:
    with open(diff_path, "r", encoding="utf-8") as f:
        diff_text = f.read()

    stats = DiffStats()

    for line in diff_text.splitlines():
        if line.startswith("+") and "(wire" in line:
            stats.wire_added += 1
        elif line.startswith("-") and "(wire" in line:
            stats.wire_removed += 1
        elif line.startswith("+") and "(segment" in line:
            stats.track_added += 1
        elif line.startswith("-") and "(segment" in line:
            stats.track_removed += 1

    return stats

from lark import Lark, Transformer, Token, Tree
from dataclasses import dataclass, field
from typing import Optional
import re

#dataclass
@dataclass
class DiffStats:
    wire_added: int = 0
    wire_removed: int = 0
    wire_modified: int = 0
    track_added: int = 0
    track_removed: int = 0
    track_modified: int = 0

@dataclass
class DiffLine:
    #representation of diffs, content are lines without +/-
    kind: str #can be either added, removed or context
    content: str

@dataclass
class DiffHunk:
    #hunk = connected changeblock lead by @@-12,7 +12,8 @@
    lines: list[DiffLine] = field(default_factory=list)

@dataclass
class ChangeSet:
    #solution of pairing logic for each hunk
    added: list[str] = field(default_factory=list)
    removed: list[str] = field(default_factory=list)
    modified: list[tuple[str, str]] = field(default_factory=list)

#lark grammar for git diff
#rules: small letters describing structure, becoming treeknot
#terminals: big letters describing single textparts per REGEX, becoming leafs
#diff built out of multiple blocks, + meaning at least one
#one block = one changes file with exactly one file header and at least one hunk
#file header has many lines
#hunk = hunk header and then beliebig viele * -> 0 or more lines
#[^\n]* any number of symbols expcept newline
#(?!\+\+) neg. lookahead, only one + not two additional
#=> similar to removed
#context every line which are starting with a space
#sometimes in diff there are No new line at end of file which need to be ignored
DIFF_GRAMMAR = r"""
    start: block+

    block: file_header hunk+

    file_header: DIFF_LINE INDEX_LINE OLD_FILE NEW_FILE

    hunk: hunk_header line*

    hunk_header: HUNK_HEADER

    line: added_line
        | removed_line
        | context_line

    added_line:   ADDED
    removed_line: REMOVED
    context_line: CONTEXT

    DIFF_LINE:   /diff --git[^\n]*\n/
    INDEX_LINE:  /index[^\n]*\n/
    OLD_FILE:    /---[^\n]*\n/
    NEW_FILE:    /\+\+\+[^\n]*\n/
    HUNK_HEADER: /@@ [^\n]* @@[^\n]*\n/

    ADDED:   /\+(?!\+\+)[^\n]*\n?/
    REMOVED: /-(?!--)[^\n]*\n?/
    CONTEXT: / [^\n]*\n?/

    %ignore /\\ No newline at end of file\n?/
"""
#lark building our of this a syntax tree, DiffTransofmer can use this tree
#to built it from bottum to top in python objects, each method in transfoermer
#is equal to one rule in grammar

diff_parser = Lark(DIFF_GRAMMAR, parser="earley", start="start")

KICAD_TYPES = {"wire", "segment"}

def classify_kicad_line(content: str) -> Optional[str]:
    stripped = content.strip()
    for t in KICAD_TYPES:
        if stripped.startswith(f"({t}") or stripped.startswith(f"({t}\n"):
            return t
    return None

class DiffTransformer(Transformer):
    def added_line(self, items):
        raw = str(items[0])
        return DiffLine(kind="added", content=raw[1:].rstrip("\n"))

    def removed_line(self, items):
        raw = str(items[0])
        return DiffLine(kind="removed", content=raw[1:].rstrip("\n"))

    def context_line(self, items):
        raw = str(items[0])
        return DiffLine(kind="context", content=raw[1:].rstrip("\n"))

    def line(self, items):
        return items[0]

    def hunk_header(self, items):
        return None

    def hunk(self, items):
        lines = [i for i in items if isinstance(i, DiffLine)]
        return DiffHunk(lines=lines)

    def file_header(self, items):
        return None

    def block(self, items):
        return [i for i in items if isinstance(i, DiffHunk)]

    def start(self, items):
        hunks = []
        for block in items:
            hunks.extend(block)
        return hunks

#modfied
def pair_changes(hunk: DiffHunk) -> ChangeSet:
    """
    Recognizing blocks that are built together out of removed and added lines
    in a Hunk and pair them as modigied
    """
    #logic: Git writes changes first - then +
    # - old wire a
    # + old wire a
    # => modified(olda, olda)
    # - old wire b
    # - old wire c
    # + new wire b
    #=> modified (b,b), removed(c)
    #flush is jsut to clear the buffer (buf)
    cs = ChangeSet()

    for dl in hunk.lines:
        if dl.kind == "added":
            cs.added.append(dl.content)
        elif dl.kind == "removed":
            cs.removed.append(dl.content)
    return cs

def collect_kicad_blocks(lines: list[DiffLine]) -> list[DiffLine]:
    result = []
    buffer = []
    current_kind = None
    current_type = None
    depth = 0

    for dl in lines:
        content = dl.content
        stripped = content.strip()

        if depth == 0:
            if stripped.startswith("("):
                buffer = [content]
                current_kind = dl.kind
                #remember kicad type of outer blocks
                for t in KICAD_TYPES:
                    if stripped.startswith(f"({t}"):
                        current_type = t
                        break
                else:
                    current_type = None
                depth = stripped.count("(") - stripped.count(")")
                if depth == 0:
                    result.append(DiffLine(kind=current_kind, content="\n".join(buffer)))
                    buffer = []
                    current_kind = None
                    current_type = None
            else:
                result.append(dl)
        else:
            #inside block if +/- then block is modified_block
            if dl.kind in ("added", "removed"):
                current_kind = dl.kind

            buffer.append(content)
            depth += stripped.count("(") - stripped.count(")")

            if depth <= 0:
                depth = 0
                #kicad type in content so taht classify kicad line can find
                if current_type and not buffer[0].strip().startswith(f"({current_type}"):
                    full_content = f"({current_type}\n" + "\n".join(buffer)
                else:
                    full_content = "\n".join(buffer)
                result.append(DiffLine(kind=current_kind, content=full_content))
                buffer = []
                current_kind = None
                current_type = None
    if buffer:
        full_content = "\n".join(buffer)
        if current_kind is not None:
            result.append(DiffLine(kind=current_kind, content=full_content))

    return result

def norm_diff(diff_text: str) -> str:
    return re.sub(
        r'^(new|deleted) file mode \d+\n',
        '',
        diff_text,
        flags=re.MULTILINE
        )

def count_changes(diff_path: str) -> DiffStats:
    #simple counting function adapted to new grammar logic
    with open(diff_path, "r", encoding="utf-8") as f:
        diff_text = f.read()
    
    diff_text = norm_diff(diff_text)
    tree = diff_parser.parse(diff_text)
    hunks = DiffTransformer().transform(tree)

    stats = DiffStats()

    for hunk in hunks:
        collected = collect_kicad_blocks(hunk.lines)

        hunk_collected = DiffHunk(lines=collected)
        cs = pair_changes(hunk_collected)

        for line in cs.added:
            t = classify_kicad_line(line)
            if t == "wire": stats.wire_added += 1
            elif t == "segment": stats.track_added += 1

        for line in cs.removed:
            t = classify_kicad_line(line)
            if t== "wire": stats.wire_removed += 1
            elif t == "segment": stats.track_removed += 1

    return stats

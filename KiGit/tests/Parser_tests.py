import sys
from pathlib import Path
import io

# Dadurch kann "from parser.diff_parser import KiCadDiffParser" überhaupt funktionieren
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

from parser.diff_parser import KiCadDiffParser
import scripts.BasicChange as BasicChange


class FakeBlob:
    def __init__(self, text):
        self.data_stream = io.BytesIO(text.encode())


class FakeDiff:
    def __init__(
        self,
        path,
        old_text="",
        new_text="",
        deleted=False
    ):
        self.a_path = path
        self.b_path = path

        self.a_blob = FakeBlob(old_text) if old_text else None
        self.b_blob = FakeBlob(new_text) if new_text else None

        self.deleted_file = deleted


@pytest.mark.parametrize( # Parametrisierte Tests, Jeder Tupel ein Seperater test
   "path,old_text,new_text,expected_added,expected_removed,expected_modified",
    [

        # SEGMENT TESTS (.kicad_pcb)

        # Ein vollständiger Segment-Block wurde hinzugefügt.
        # Erwartung: added = 1
        (
            "test.kicad_pcb",

            "",

            """
(kicad_pcb
  (segment
    (start (xy 0 0))
    (end (xy 10 10))
  )
)
""",

            1, 0, 0
        ),

        # Ein vollständiger Segment-Block wurde entfernt.
        # Erwartung: removed = 1
        (
            "test.kicad_pcb",

            """
(kicad_pcb
  (segment
    (start (xy 0 0))
    (end (xy 10 10))
  )
)
""",

            "",

            0, 1, 0
        ),

        # Innerhalb eines vorhandenen Segments wurde eine Koordinate geändert.
        # Erwartung: modified = 1
        (
            "test.kicad_pcb",

            """
(kicad_pcb
  (segment
    (start (xy 0 0))
    (end (xy 10 10))
  )
)
""",

            """
(kicad_pcb
  (segment
    (start (xy 1 1))
    (end (xy 10 10))
  )
)
""",

            0, 0, 1
        ),

        # Gleich wie oben, Endpunkt wurde geändert.
        # Erwartung: modified = 1
        (
            "test.kicad_pcb",

            """
(kicad_pcb
  (segment
    (start (xy 0 0))
    (end (xy 10 10))
  )
)
""",

            """
(kicad_pcb
  (segment
    (start (xy 0 0))
    (end (xy 20 20))
  )
)
""",

            0, 0, 1
        ),

        # WIRE TESTS (.kicad_sch)

        # Ein kompletter Wire-Block wurde hinzugefügt.
        (
            "test.kicad_sch",

            "",

            """
(kicad_sch
  (wire
    (pts
      (xy 0 0)
      (xy 10 10)
    )
  )
)
""",

            1, 0, 0
        ),

        # Ein kompletter Wire-Block wurde entfernt.
        (
            "test.kicad_sch",

            """
(kicad_sch
  (wire
    (pts
      (xy 0 0)
      (xy 10 10)
    )
  )
)
""",

            "",

            0, 1, 0
        ),

        # Eine Koordinate innerhalb eines Wire-Blocks wurde geändert.
        (
            "test.kicad_sch",

            """
(kicad_sch
  (wire
    (pts
      (xy 0 0)
      (xy 10 10)
    )
  )
)
""",

            """
(kicad_sch
  (wire
    (pts
      (xy 1 1)
      (xy 10 10)
    )
  )
)
""",

            0, 0, 1
        ),
    ]
) 

def test_parser_cases(
    path,
    old_text,
    new_text,
    expected_added,
    expected_removed,
    expected_modified
):

    parser = KiCadDiffParser()

    diff_index = [
        FakeDiff(
            path=path,
            old_text=old_text,
            new_text=new_text
        )
    ]

    result = parser.parse(diff_index)

    # Prüfen, ob die Anzahl erkannter Elemente stimmt
    assert len(result.getAdded()) == expected_added
    assert len(result.getRemoved()) == expected_removed
    assert len(result.getModified()) == expected_modified

def test_unknown_file_ignored():
    # Testet, ob Dateien mit "unbekannter" Endung ignoriert werden

    parser = KiCadDiffParser()

    diff_index = [
        FakeDiff(
            path="test.txt",
            old_text="test",
            new_text="test2"
        )
    ]

    result = parser.parse(diff_index)

    assert result.isEmpty()


def test_empty_diff():
    # Testet Parser bei leerer Datei

    parser = KiCadDiffParser()

    diff_index = []

    result = parser.parse(diff_index)

    assert result.isEmpty()


def test_multiple_segments_added():
    # Zwei vollständige Segment-Blöcke wurden hinzugefügt.
    # Erwartung: added = 2

    parser = KiCadDiffParser()

    diff_index = [
        FakeDiff(
            path="test.kicad_pcb",
            old_text="",
            new_text="""
(kicad_pcb
  (segment
    (start (xy 0 0))
    (end (xy 10 10))
  )
  (segment
    (start (xy 20 20))
    (end (xy 30 30))
  )
)
"""
        )
    ]

    result = parser.parse(diff_index)

    assert len(result.getAdded()) == 2
    assert len(result.getRemoved()) == 0
    assert len(result.getModified()) == 0


def test_multiple_files():
    # Ein Segment und ein Wire wurden hinzugefügt.
    # Erwartung: added = 2

    parser = KiCadDiffParser()

    diff_index = [
        FakeDiff(
            path="board.kicad_pcb",
            new_text="""
(kicad_pcb
  (segment
    (start (xy 0 0))
    (end (xy 10 10))
  )
)
"""
        ),
        FakeDiff(
            path="schematic.kicad_sch",
            new_text="""
(kicad_sch
  (wire
    (pts
      (xy 0 0)
      (xy 10 10)
    )
  )
)
"""
        )
    ]

    result = parser.parse(diff_index)

    assert len(result.getAdded()) == 2
    assert len(result.getRemoved()) == 0
    assert len(result.getModified()) == 0


def test_mixed_changes_same_file():
    # Ein Segment wurde verändert.
    # Erwartung: modified = 1

    parser = KiCadDiffParser()

    diff_index = [
        FakeDiff(
            path="test.kicad_pcb",
            old_text="""
(kicad_pcb
  (segment
    (start (xy 0 0))
    (end (xy 10 10))
  )
)
""",
            new_text="""
(kicad_pcb
  (segment
    (start (xy 20 20))
    (end (xy 30 30))
  )
)
"""
        )
    ]

    result = parser.parse(diff_index)

    assert len(result.getAdded()) == 1
    assert len(result.getRemoved()) == 1
    assert len(result.getModified()) == 0
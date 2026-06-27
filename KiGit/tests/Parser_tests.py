import sys
from pathlib import Path

# Dadurch kann "from parser.new_parser import KiCadDiffParser" überhaupt funktionieren
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest # für Tests
from parser.diff_parser import KiCadDiffParser # um Parser zu bekommen


@pytest.mark.parametrize( # Parametrisierte Tests, Jeder Tupel ein Seperater test
    "diff_content,expected_added,expected_removed,expected_modified",
    [
        # SEGMENT TESTS (.kicad_pcb)

        # Ein vollständiger Segment-Block wurde hinzugefügt.
        # Erwartung: added = 1
        (
            """diff --git a/test.kicad_pcb b/test.kicad_pcb
--- a/test.kicad_pcb
+++ b/test.kicad_pcb
@@ -1,0 +1,4 @@
+(segment
+  (start 0 0)
+  (end 10 10)
+)
""",
            1, 0, 0
        ),

        # Ein vollständiger Segment-Block wurde entfernt.
        # Erwartung: removed = 1
        (
            """diff --git a/test.kicad_pcb b/test.kicad_pcb
--- a/test.kicad_pcb
+++ b/test.kicad_pcb
@@ -1,4 +0,0 @@
-(segment
-  (start 0 0)
-  (end 10 10)
-)
""",
            0, 1, 0
        ),

        # Innerhalb eines vorhandenen Segments wurde ein Wert geändert.
        # Erwartung: changed = 1
        (
            """diff --git a/test.kicad_pcb b/test.kicad_pcb
--- a/test.kicad_pcb
+++ b/test.kicad_pcb
@@ -1,4 +1,4 @@
 (segment
-  (start 0 0)
+  (start 1 1)
   (end 10 10)
 )
""",
            0, 0, 1
        ),

        # gleich wie oben, Test um zu schauen ob Modified Segments einen fehler hatte
        (
            """diff --git a/test.kicad_pcb b/test.kicad_pcb
--- a/test.kicad_pcb
+++ b/test.kicad_pcb
@@ -1,4 +1,4 @@
 (segment
   (start 0 0)
-  (end 10 10)
+  (end 20 20)
 )
""",
            0, 0, 1
        ),

        # WIRE TESTS (.kicad_sch)

        # Ein kompletter Wire-Block wurde hinzugefügt.
        (
            """diff --git a/test.kicad_sch b/test.kicad_sch
--- a/test.kicad_sch
+++ b/test.kicad_sch
@@ -1,0 +1,5 @@
+(wire
+  (pts
+    (xy 0 0) (xy 10 10)
+  )
+)
""",
            1, 0, 0
        ),

        # Ein kompletter Wire-Block wurde entfernt.
        (
            """diff --git a/test.kicad_sch b/test.kicad_sch
--- a/test.kicad_sch
+++ b/test.kicad_sch
@@ -1,5 +0,0 @@
-(wire
-  (pts
-    (xy 0 0) (xy 10 10)
-  )
-)
""",
            0, 1, 0
        ),

        # Eine Koordinate innerhalb eines Wire-Blocks wurde geändert.
        (
            """diff --git a/test.kicad_sch b/test.kicad_sch
--- a/test.kicad_sch
+++ b/test.kicad_sch
@@ -1,5 +1,5 @@
 (wire
   (pts
-    (xy 0 0) (xy 10 10)
+    (xy 1 1) (xy 10 10)
   )
 )
""",
            0, 0, 1
        ),
    ]
)

def test_parser_cases(
    diff_content,
    expected_added,
    expected_removed,
    expected_modified
):

    parser = KiCadDiffParser()

    result = parser.parse(diff_content)

    # Prüfen, ob die Anzahl erkannter Elemente stimmt
    assert len(result.getAdded()) == expected_added
    assert len(result.getRemoved()) == expected_removed
    assert len(result.getModified()) == expected_modified


def test_unknown_file_ignored(): # Testet, ob Datein mit "unbekannter" Endung ignoriert werden

    diff_content = """diff --git a/test.txt b/test.txt
--- a/test.txt
+++ b/test.txt
@@ -1 +1 @@
-test
+test2
"""

    parser = KiCadDiffParser()

    result = parser.parse(diff_content)

    assert result.isEmpty()


def test_empty_diff(): # Testet Parser bei leerer Datei

    parser = KiCadDiffParser()

    result = parser.parse("")

    assert result.isEmpty()


def test_multiple_segments_added():
    # Zwei vollständige Segment-Blöcke wurden hinzugefügt.
    # Erwartung: added = 2

    diff_content = """diff --git a/test.kicad_pcb b/test.kicad_pcb
--- a/test.kicad_pcb
+++ b/test.kicad_pcb
@@ -1,0 +1,8 @@
+(segment
+  (start 0 0)
+  (end 10 10)
+)
+(segment
+  (start 20 20)
+  (end 30 30)
+)
"""

    parser = KiCadDiffParser()

    result = parser.parse(diff_content)

    assert len(result.getAdded()) == 2
    assert len(result.getRemoved()) == 0
    assert len(result.getModified()) == 0


def test_multiple_files():
    # Ein Segment und ein Wire wurden hinzugefügt.
    # Erwartung: added = 2

    diff_content = """diff --git a/board.kicad_pcb b/board.kicad_pcb
--- a/board.kicad_pcb
+++ b/board.kicad_pcb
@@ -1,0 +1,4 @@
+(segment
+  (start 0 0)
+  (end 10 10)
+)
diff --git a/schematic.kicad_sch b/schematic.kicad_sch
--- a/schematic.kicad_sch
+++ b/schematic.kicad_sch
@@ -1,0 +1,5 @@
+(wire
+  (pts
+    (xy 0 0) (xy 10 10)
+  )
+)
"""

    parser = KiCadDiffParser()

    result = parser.parse(diff_content)

    assert len(result.getAdded()) == 2
    assert len(result.getRemoved()) == 0
    assert len(result.getModified()) == 0

def test_mixed_changes_same_file():
    # Ein Segment wurde hinzugefügt und eines entfernt.
    # Erwartung: added = 1, removed = 1

    diff_content = """diff --git a/test.kicad_pcb b/test.kicad_pcb
--- a/test.kicad_pcb
+++ b/test.kicad_pcb
@@ -1,4 +1,4 @@
-(segment
-  (start 0 0)
-  (end 10 10)
-)
+(segment
+  (start 20 20)
+  (end 30 30)
+)
"""

    parser = KiCadDiffParser()

    result = parser.parse(diff_content)

    assert len(result.getAdded()) == 1
    assert len(result.getRemoved()) == 1
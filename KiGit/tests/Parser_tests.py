import sys
from pathlib import Path
# Dadurch kann "from parser.new_parser import KiCadDiffParser" überhaupt funktionieren
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import tempfile # für temporäre Diff-Dateien der Tests
import pytest # für Tests
from parser.new_parser import KiCadDiffParser # um Parser zu bekommen

def create_temp_diff(content: str) -> str: # da Parser Dateipfad erwartet, dazu Difftext in diese Datei
    temp = tempfile.NamedTemporaryFile(
        delete=False, # Datei bleibt erhalten, Parser kann diese benutzen
        suffix=".diff",
        mode="w",
        encoding="utf-8"
    )

    temp.write(content)  # Diff-Inhalt in die Datei schreiben

    temp.close() # Datei schließen, damit andere Prozesse sie lesen können

    return temp.name # Pfad zurückgeben

# Parametrisierter Test:
# pytest führt dieselbe Testfunktion mehrfach aus.
# Jeder Tupel-Eintrag in der Liste entspricht einem separaten Testfall.
@pytest.mark.parametrize( # Parametrisierte Tests, Jeder Tupel ein Seperater test
    "diff_content,expected_added,expected_removed,expected_modified",
    [
        # SEGMENT TESTS (.kicad_pcb)

        # Ein vollständiger Segment-Block wurde hinzugefügt.
        # Erwartung: added = 1
        (
            """diff --git a/test.kicad_pcb b/test.kicad_pcb
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

    diff_path = create_temp_diff(diff_content) # Diff-Datei für den aktuellen Testfall erzeugen

    parser = KiCadDiffParser(diff_path)

    results = parser.parse(diff_path)

    assert len(results) == 1

    result = results[0].result

    # Prüfen, ob die Anzahl erkannter Elemente stimmt
    assert result.added == expected_added
    assert result.removed == expected_removed
    assert result.changed == expected_modified

def test_unknown_file_ignored(): # Testet, ob Datein mit "unbekannter" Endung ignoriert werden

    diff_content = """diff --git a/test.txt b/test.txt
@@ -1 +1 @@
-test
+test2
"""

    diff_path = create_temp_diff(diff_content)

    parser = KiCadDiffParser(diff_path)

    results = parser.parse(diff_path)
    # Erwartung: keine Parser-Ergebnisse
    assert results == []

def test_empty_diff(): # Testet Parser bei leerer Datei

    diff_path = create_temp_diff("")

    parser = KiCadDiffParser(diff_path)

    results = parser.parse(diff_path)

    # Erwartung: keine Ergebnisse
    assert results == []
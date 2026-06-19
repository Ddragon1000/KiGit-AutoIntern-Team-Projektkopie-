import unittest
from unittest.mock import patch, MagicMock
import os

from Git_Commands import TMP_DIR
from Git_Commands import gitDiff

import pathlib

#Missing docstring in public module

class TestGitStatus(unittest.TestCase):

    #Missing type annotation for function argument `mock_run`
    @patch("Git_Commands.subprocess.run")
    def test_git_status_creates_file(self, mock_run) -> None:

        # Fake subprocess result
        mock_process = MagicMock()
        mock_process.stdout = "On branch main"
        mock_run.return_value = mock_process

        #Ruff rule F821 Undefined name `gitStatus`
        # Funktion ausführen
        result = gitStatus()

        # Prüfen ob Rückgabe stimmt
        #https://docs.astral.sh/ruff/rules/pytest-unittest-assertion/
        #Use a regular `assert` instead of unittest-style `assertEqual`
        self.assertEqual(result, 0)


        #`os.path.join()` should be replaced by `Path` with `/` operator
        # Prüfen ob Datei existiert
        filepath = os.path.join(TMP_DIR, "git_status.txt")
        #https://docs.astral.sh/ruff/rules/pytest-unittest-assertion/
        #Use a regular `assert` instead of unittest-style `assertTrue`
        self.assertTrue(pathlib.Path(filepath).exists())

        #`open()` should be replaced by `Path.open()`
        # Inhalt prüfen
        #with pathlib.Path(filepath).open(encoding="utf-8") as f:
        #    content = f.read()
        content = pathlib.Path(filepath).read_text(encoding="utf-8")

        #https://docs.astral.sh/ruff/rules/pytest-unittest-assertion/
        #Use a regular `assert` instead of unittest-style `assertIn`
        self.assertIn("On branch main", content)


if __name__ == "__main__":
    unittest.main()
class TestGitDiff(unittest.TestCase):

    @patch("Git_Commands.subprocess.run")
    def test_git_diff_creates_output_file(self, mock_run) -> None:

        mock_process = MagicMock()
        mock_process.stdout = "diff --git a/test.txt b/test.txt"

        mock_run.return_value = mock_process

        result = gitDiff("test.txt")

        #https://docs.astral.sh/ruff/rules/pytest-unittest-assertion/
        #Use a regular `assert` instead of unittest-style `assertEqual`
        self.assertEqual(result, 0)

        filepath = os.path.join(
            TMP_DIR,
            "tmp_test.txt.txt",
        )

        #Replace with `Path(...).exists()`
        self.assertTrue(pathlib.Path(filepath).exists())

        #error[FURB101][*]: `open` and `read` should be replaced by `Path(filepath).read_text(encoding="utf-8")`
        #with pathlib.Path(filepath).open(encoding="utf-8") as f:
        #    content = f.read()
        content = pathlib.Path(filepath).read_text(encoding="utf-8")

        #https://docs.astral.sh/ruff/rules/pytest-unittest-assertion/
        #Use a regular `assert` instead of unittest-style `assertIn`
        self.assertIn("diff --git", content)


if __name__ == "__main__":
    unittest.main()

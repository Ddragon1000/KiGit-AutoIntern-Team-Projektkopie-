import unittest
from unittest.mock import patch, MagicMock
import os

from Git_Commands import TMP_DIR
from Git_Commands import gitDiff

class TestGitStatus(unittest.TestCase):

    @patch("Git_Commands.subprocess.run")
    def test_git_status_creates_file(self, mock_run):

        # Fake subprocess result
        mock_process = MagicMock()
        mock_process.stdout = "On branch main"
        mock_run.return_value = mock_process

        # Funktion ausführen
        result = gitStatus()

        # Prüfen ob Rückgabe stimmt
        self.assertEqual(result, 0)

        # Prüfen ob Datei existiert
        filepath = os.path.join(TMP_DIR, "git_status.txt")
        self.assertTrue(os.path.exists(filepath))

        # Inhalt prüfen
        with open(filepath, encoding="utf-8") as f:
            content = f.read()

        self.assertIn("On branch main", content)


if __name__ == "__main__":
    unittest.main()
class TestGitDiff(unittest.TestCase):

    @patch("Git_Commands.subprocess.run")
    def test_git_diff_creates_output_file(self, mock_run):

        mock_process = MagicMock()
        mock_process.stdout = "diff --git a/test.txt b/test.txt"

        mock_run.return_value = mock_process

        result = gitDiff("test.txt")

        self.assertEqual(result, 0)

        filepath = os.path.join(
            TMP_DIR,
            "tmp_test.txt.txt",
        )

        self.assertTrue(os.path.exists(filepath))

        with open(filepath, encoding="utf-8") as f:
            content = f.read()

        self.assertIn("diff --git", content)


if __name__ == "__main__":
    unittest.main()

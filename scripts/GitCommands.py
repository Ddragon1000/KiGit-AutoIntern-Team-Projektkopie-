import subprocess
import platform
import os

shell = platform.system() == "Windows"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMP_DIR = os.path.join(ROOT, "tmp")

def gitDiff(f: str, commit: str = None):
    if commit:
        cmd = ["git", "diff", commit, f]
    else:
        cmd = ["git", "diff", f]

    diff = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        shell=shell
    )

    os.makedirs(TMP_DIR, exist_ok=True)
    filename = f.replace("/", "_").replace("\\", "_")

    with open(os.path.join(TMP_DIR, f"tmp_{filename}.txt"), "w", encoding="utf-8") as k:
        k.write(diff.stdout)
    return 0

def gitStatus():
    pass

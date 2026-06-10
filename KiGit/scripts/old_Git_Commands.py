import subprocess
import platform
import os
import sys

shell = platform.system() == "Windows"
ROOT = os.getcwd()
TMP_DIR = os.path.join(os.path.expanduser("~"), ".kigit", "tmp")


def gitDiff(f: str, commit: str = None, debug: bool = False):
    if commit:
        cmd = ["git", "diff", commit, "--", f]
    else:
        cmd = ["git", "diff", f]
    
    if debug:    
        print(f"[DEBUG] cwd: {ROOT}")
        print(f"[DEBUG] cmd: {' '.join(cmd)}")

    try:
        diff = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            shell=shell,
            cwd=ROOT
        )
    except subprocess.CalledProcessError as e:
        print(f"[Git-ERROR] The command failed: {e.stderr}", file=sys.stderr)
    
    if debug:
        print(f"[DEBUG] stdout length: {len(diff.stdout)}")
        print(f"[DEBUG] stderr: {diff.stderr}")

    os.makedirs(TMP_DIR, exist_ok=True)
    filename = os.path.basename(f).replace(".", "_")

    with open(os.path.join(TMP_DIR, f"tmp_{filename}.txt"), "w", encoding="utf-8") as k:
        k.write(diff.stdout)
    return 0


def gitStatus():
    cmd = ["git", "status"]

    status = subprocess.run(cmd, capture_output=True, text=True, shell=shell, cwd=ROOT)

    os.makedirs(TMP_DIR, exist_ok=True)

    with open(os.path.join(TMP_DIR, "git_status.txt"), "w", encoding="utf-8") as k:
        k.write(status.stdout)
    return 0

import subprocess
import pathlib
import os
import re
import time
from shutil import which
from scripts.DiffResRenderer import FaultyFileOutput
from scripts.DiffRes import DiffRes

from scripts.commands import GitManager


cwd = pathlib.Path.cwd()


def faultyFileDetection() -> bool:
    #faulty file detection
    
    gitmanager = GitManager(cwd)

    kicad_files = []

    for f in os.listdir(gitmanager.repo.working_tree_dir):
        if os.path.isfile(os.path.join(gitmanager.repo.working_tree_dir, f)) and (re.search("sch$", f) or re.search("pcb$", f)):
            kicad_files.append(f)

    for file in kicad_files:

        result = create_subprocess(file, False)

        file_to_delete = None

        if not result:
            print("Subprocess creation for faultyFileDetection failed. Please check if kicad-cli is installed in PATH.")
            time.sleep(5)
            break

        for arg in result.args:
            re_obj = re.search("^faultyFileCheck", arg)
            if re_obj:
                file_to_delete = re_obj.string

        if os.path.exists(os.path.join(gitmanager.repo.working_tree_dir, file_to_delete)):
            os.remove(os.path.join(gitmanager.repo.working_tree_dir, file_to_delete))


        if result.stderr:
            result.stderr = None
            return True

    return False


def erc_drc(erc_drc_output, diffres):

    filesd = diffres.filterFile()

    changed_files = [file.changes[0].origin for file in filesd]

    for file in changed_files:
        result = create_subprocess(file, True)

        if not result:
            print("Subprocess creation for erc-drc-check failed. Please check if kicad-cli is installed in PATH.")
            time.sleep(5)
            break

        if result.stderr:
            result.stderr = None
            return True

        file_check = [file, result.stdout]
        if re.search("sch$", file):
            erc_drc_output.add_schematic(file_check)
        elif re.search("pcb$", file):
            erc_drc_output.add_pcb(file_check)



def create_subprocess(file, erc_drc_check):
            
    schematic = re.search("sch$", file)
    pcb = re.search(f"pcb$", file)

    if erc_drc_check:
        if schematic:
            try:
                erc_args = ["kicad-cli", "sch", "erc", file]
                return subprocess.run(erc_args, capture_output=True, check=False, text=True)
            except:
                pass
        elif pcb:
            try:
                drc_args = ["kicad-cli", "pcb", "drc", file]
                return subprocess.run(drc_args, capture_output=True, check=False, text=True)
            except:
                pass

    else:
        if schematic:
            try:
                erc_args = ["kicad-cli", "sch", "export", "pdf", file, "--output", "faultyFileCheckSch"]
                return subprocess.run(erc_args, capture_output=True, check=False, text=True)
            except:
                pass
        elif pcb:
            try:
                drc_args = ["kicad-cli", "pcb", "export", "pdf", file, "--output", "faultyFileCheckPCB", "--layers", "F.Cu"]
                return subprocess.run(drc_args, capture_output=True, check=False, text=True)
            except:
                pass


    return None


# Source - https://stackoverflow.com/a/34177358
# Posted by Six, modified by community. See post 'Timeline' for change history
# Retrieved 2026-08-19, License - CC BY-SA 4.0

def is_tool(name):
    """Check whether `name` is on PATH and marked as executable."""

    # from whichcraft import which

    return which(name) is not None



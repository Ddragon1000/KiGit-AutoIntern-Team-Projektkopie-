import subprocess
import pathlib
import os
import re
import multiprocessing
from scripts.DiffResRenderer import FaultyFileOutput, OutputFormat
from scripts.DiffRes import DiffRes

from scripts.commands import GitManager


cwd = pathlib.Path.cwd()


def faultyFileDetection() -> bool:
    #faulty file detection
    
    gitmanager = GitManager(cwd)

    kicad_files = []

    faulty = False

    for f in os.listdir(gitmanager.repo.working_tree_dir):
        if os.path.isfile(os.path.join(gitmanager.repo.working_tree_dir, f)) and (re.search("sch$", f) or re.search("pcb$", f)):
            kicad_files.append(f)

    processes = []
    is_faulty = False
    queue = multiprocessing.Queue()
    queue.put(is_faulty)
    
    for file in kicad_files:


        p = multiprocessing.Process(target = detection, args = (file, gitmanager, queue))
        processes.append(p)

    for process in processes:
        process.start()

    for process in processes:
        process.join()
        value = queue.get()
        print(value)
        if value == True:
            faulty = True

    return faulty



def detection(file, gitmanager, queue) -> bool:
        result = create_subprocess(file, False)

        file_to_delete = ""

        if not result:
            print("Subprocess creation for faultyFileDetection failed. Please check if kicad-cli is installed in PATH.")

        for arg in result.args:
            re_obj = re.search(f"{file}.kigittmp", arg)
            if re_obj:
                file_to_delete = re_obj.string

        if os.path.exists(os.path.join(gitmanager.repo.working_tree_dir, file_to_delete)):
            os.remove(os.path.join(gitmanager.repo.working_tree_dir, file_to_delete))


        if result.stderr:
            result.stderr = None
            queue.put(True)
        else:  
            queue.put(False)


def erc_drc(erc_drc_output, diffres, output):

    filesd = diffres.filterFile()

    changed_files = [file.changes[0].origin for file in filesd]

    for file in changed_files:
        result = create_subprocess(file, True, output)

        if not result:
            print("Subprocess creation for erc-drc-check failed. Please check if kicad-cli is installed in PATH.")
            break

        if result.stderr:
            result.stderr = None
            return True

        file_check = [file, result.stdout]
        if re.search("sch$", file):
            erc_drc_output.add_schematic(file_check)
        elif re.search("pcb$", file):
            erc_drc_output.add_pcb(file_check)



def create_subprocess(file, erc_drc_check, output = None):
            
    schematic = re.search("sch$", file)
    pcb = re.search("pcb$", file)

    if not erc_drc_check:
        try:
            if schematic:
                args = ["kicad-cli", "sch", "export", "pdf", file, "--output", f"{file}.kigittmp"]
            elif pcb:
                args = ["kicad-cli", "pcb", "export", "pdf", file, "--output", f"{file}.kigittmp", "--layers", "F.Cu"]
            return subprocess.run(args, capture_output=True, check=False, text=True)
        except:
            pass
    else:
        try:
            if output == OutputFormat.TABLE:
                if schematic:
                    args = ["kicad-cli", "sch", "erc", file]
                elif pcb:
                    args = ["kicad-cli", "pcb", "drc", file]
            elif output == OutputFormat.JSON:
                if schematic:
                    args = ["kicad-cli", "sch", "erc", file, "--output", f"{file.rsplit(".", 1)[0]}-erc.json", "--format", "json"]
                elif pcb:
                    args = ["kicad-cli", "pcb", "drc", file, "--output", f"{file.rsplit(".", 1)[0]}-drc.json", "--format", "json"]
            elif output == OutputFormat.HTML:
                if schematic:
                    args = ["kicad-cli", "sch", "erc", file, "--output", f"{file.rsplit(".", 1)[0]}-erc.html"]
                elif pcb:
                    args = ["kicad-cli", "pcb", "drc", file, "--output", f"{file.rsplit(".", 1)[0]}-drc.html"]
            return subprocess.run(args, capture_output=True, check=False, text=True)
        except:
            pass
  

    return None






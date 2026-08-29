import subprocess
import pathlib
import os
import re
import concurrent.futures
from scripts.DiffResRenderer import FaultyOutput, ERC_DRC_Output, OutputFormat
from scripts.DiffRes import DiffRes

from scripts.commands import GitManager


FILE_POSITION_FAULTY_FILE_DETECTION = 4
FILE_POSITION_ERC_DRC = 3
cwd = pathlib.Path.cwd()


def faultyFileDetection() -> bool:
    #faulty file detection
    
    gitmanager = GitManager(cwd)

    kicad_files = []

    for f in os.listdir(gitmanager.repo.working_tree_dir):
        if os.path.isfile(os.path.join(gitmanager.repo.working_tree_dir, f)) and (re.search("sch$", f) or re.search("pcb$", f)):
            kicad_files.append(f)

    is_faulty = False

    with concurrent.futures.ProcessPoolExecutor() as executor:
        results = executor.map(create_faulty_file_check_subprocess, kicad_files)


        for result in list(results):

            if not result:
                subprocess_failed_output = FaultyOutput()
                subprocess_failed_output.subprocess_faulty_output()
                break

            file_to_delete = ""

            file_to_delete = f"{result.args[FILE_POSITION_FAULTY_FILE_DETECTION]}.kigittmp"

            if os.path.exists(os.path.join(gitmanager.repo.working_tree_dir, file_to_delete)):
                os.remove(os.path.join(gitmanager.repo.working_tree_dir, file_to_delete))


            if result.stderr:
                result.stderr = None
                is_faulty = True


    return is_faulty



def erc_drc_func(erc_drc_output, diffres, output) -> bool:

    filesd = diffres.filterFile()

    changed_files = [file.changes[0].origin for file in filesd]

    func_args = [[file, output] for file in changed_files]

    is_faulty = False

    with concurrent.futures.ProcessPoolExecutor() as executor:
        results = executor.map(create_erc_drc_subprocess, func_args)

        for result in list(results):

            if not result:
                subprocess_failed_output = FaultyOutput()
                subprocess_failed_output.subprocess_faulty_output()
                break

            if result.stderr:
                result.stderr = None
                is_faulty = True

            file = result.args[FILE_POSITION_ERC_DRC]
            file_check = [file, result.stdout]
            if re.search("[.]kicad_sch$", file):
                erc_drc_output.add_schematic(file_check)
            elif re.search("[.]kicad_pcb$", file):
                erc_drc_output.add_pcb(file_check)

        
    return is_faulty



def create_faulty_file_check_subprocess(file):
            
    schematic = re.search("[.]kicad_sch$", file)
    pcb = re.search("[.]kicad_pcb$", file)

    try:
        if schematic:
            args = ["kicad-cli", "sch", "export", "pdf", file, "--output", f"{file}.kigittmp"]
        elif pcb:
            args = ["kicad-cli", "pcb", "export", "pdf", file, "--output", f"{file}.kigittmp", "--layers", "F.Cu"]
        return subprocess.run(args, capture_output=True, check=False, text=True)
    except:
        pass
    return None



def create_erc_drc_subprocess(func_args):

    file = func_args[0]
    output = func_args[1]

    schematic = re.search("[.]kicad_sch$", file)
    pcb = re.search("[.]kicad_pcb$", file)


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


def find_kicad_cli() -> str:
    look_for = "kicad-cli.exe"

    drives = [f'{letter}:\\' for letter in 'CDEFGHIJKLMNOPQRSTUVWXYZ']
    for drive in drives:
        if os.path.isdir(drive):
            for root, dirs, files in os.walk(drive):
                if look_for in files:
                    return os.path.join(root, look_for)
    return ""






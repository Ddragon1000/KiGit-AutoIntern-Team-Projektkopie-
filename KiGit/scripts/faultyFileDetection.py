import subprocess
import pathlib
import os
import re
import multiprocessing
import concurrent.futures
from scripts.DiffResRenderer import FaultyOutput, ERC_DRC_Output, OutputFormat
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
    subprocess_failed = False
    queue2 = multiprocessing.Queue()
    queue2.put(subprocess_failed)

    for file in kicad_files:
        p = multiprocessing.Process(target = detection, args = (file, gitmanager, queue, queue2))
        processes.append(p)

    for process in processes:
        process.start()

    subprocess_fail = queue2.get()
    if subprocess_fail:
        for process in processes:
            process.close()
    else:
        for process in processes:
            process.join()
            value = queue.get()
            if value == True:
                faulty = True

    return faulty



def detection(file, gitmanager, queue, queue2):
    result = create_faulty_file_check_subprocess(file)

    file_to_delete = ""

    if not result:
        queue2.put(True)
        subprocess_failed_output = FaultyOutput()
        subprocess_failed_output.subprocess_faulty_output()
        return

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

            if result.stderr:
                result.stderr = None
                is_faulty = True

            file = result.args[3]
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
            for drive in drives:
                for root, dirs, files in os.walk(drive):
                    if look_for in files:
                        return os.path.join(root, look_for)
    return ""






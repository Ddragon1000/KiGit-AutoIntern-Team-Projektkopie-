import subprocess
import pathlib
import os
import re
from scripts.DiffResRenderer import FaultyFileOutput

from kigit_globals import FILE_ENDINGS
from scripts.commands import GitManager


cwd = pathlib.Path.cwd()


def faultyFileDetection(faulty_file_output: FaultyFileOutput) -> bool:
    #faulty file detection
    
    gitmanager = GitManager(cwd)
    faulty_file_exists = False # variable to check if there was a faulty file found or not


    kicad_files = []

    for kicad_ending in FILE_ENDINGS.values():
        for f in os.listdir(gitmanager.repo.working_tree_dir):
            if os.path.isfile(os.path.join(gitmanager.repo.working_tree_dir, f)) and re.search(f"{kicad_ending}$", f):
                kicad_files.append(f)

    

    file_endings = FILE_ENDINGS

    for file in kicad_files:

        erc_args = ["kicad-cli", "sch", "erc", file]
        drc_args = ["kicad-cli", "pcb", "drc", file]

        result = None

        schematic = re.search(f"{file_endings["sch"]}$", file)
        pcb = re.search(f"{file_endings["pcb"]}$", file)
        
        if schematic:    
            result = subprocess.run(erc_args, capture_output=True, check=False, text=True)
        elif pcb:    
            result = subprocess.run(drc_args, capture_output=True, check=False, text=True)

        if result.stderr:
            faulty_file_exists = True
            faulty = True
            erc_drc_output = None

            file_check = [file, faulty, erc_drc_output] # list of output relevant information [file, faulty, result.stdout for erc_drc_check in this case none]
            
            if schematic:
                faulty_file_output.add_schematic(file_check)
            elif pcb:
                faulty_file_output.add_pcb(file_check)

            result.stderr = None

        elif result.stdout:
            faulty = False
            erc_drc_output = result.stdout
                
            file_check = [file, faulty, erc_drc_output] # list of output relevant information [file, faulty, result.stdout for erc_drc_check]
            
            if re.search(f"{file_endings["sch"]}$", file):
                faulty_file_output.add_schematic(file_check)
            elif re.search(f"{file_endings["pcb"]}$", file):
                faulty_file_output.add_pcb(file_check)

            
    return faulty_file_exists




    


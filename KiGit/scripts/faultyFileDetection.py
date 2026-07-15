import subprocess
import os
import re
from scripts.DiffResRenderer import FaultyFileOutput

from kigit_globals import FILE_PARSERS
from scripts.commands import GitManager


cwd = os.getcwd()


def faultyFileDetection(erc_drc_check: bool, faulty_file_check: bool, faulty_file_output: FaultyFileOutput) -> bool:
    #faulty file detection
    
    gitmanager = GitManager(cwd)
    faultyFile = False # variable to check if there was a fualty file found or not

    kicad_files_endings = FILE_PARSERS.keys()
   
    count = 0
    schematic = None
    pcb = None

    for key in FILE_PARSERS.keys():
        count += 1
        if count == 1:
            schematic = key
        if count == 2:
            pcb = key

    
    sch_files = [f for f in os.listdir(gitmanager.repo.working_tree_dir) 
                 if os.path.isfile(os.path.join(gitmanager.repo.working_tree_dir, f)) and re.search(f"{schematic}$", f)]
    pcb_files = [f for f in os.listdir(gitmanager.repo.working_tree_dir) 
                 if os.path.isfile(os.path.join(gitmanager.repo.working_tree_dir, f)) and re.search(f"{pcb}$", f)]
    
    if faulty_file_check:
        for file in sch_files:
            args = ["kicad-cli", "sch", "erc", file]

            result = subprocess.run(args, capture_output=True, check=False, text=True)

            if result.stderr:
                faultyFile = True
                file_check = [file, True, False, None] # list of output relevant information [file, faulty_file, erc_drc_check, result.stdout for erc_drc_check]
                faulty_file_output.add_schematic(file_check)
            elif erc_drc_check:
                file_check = [file, False, True, result.stdout]
                faulty_file_output.add_schematic(file_check)
            else:
                file_check = [file, False, False, None]
                faulty_file_output.add_schematic(file_check)

        for file in pcb_files:
            args = ["kicad-cli", "pcb", "drc", file]

            result = subprocess.run(args, capture_output=True, check=False, text=True)

            if result.stderr:
                faultyFile = True
                file_check = [file, True, False, None]
                faulty_file_output.add_pcb(file_check)
            elif erc_drc_check: 
                file_check = [file, False, True, result.stdout]
                faulty_file_output.add_pcb(file_check)
            else:
                file_check = [file, False, False, None]
                faulty_file_output.add_pcb(file_check)

            
        return faultyFile


    elif erc_drc_check:
        for file in sch_files:
            args = ["kicad-cli", "sch", "erc", file]

            result = subprocess.run(args, capture_output=True, check=False, text=True)

            print(f"ERC check: \n{result.stdout}")
            file_check = []

        for file in pcb_files:
            args = ["kicad-cli", "pcb", "drc", file]

            result = subprocess.run(args, capture_output=True, check=False, text=True)

            print(f"DRC check: \n{result.stdout}")
        
        return False


    


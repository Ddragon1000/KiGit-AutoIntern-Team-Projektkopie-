import subprocess
import os
import re

from kigit_globals.py import FILE_PARSERS
from scripts.commands import GitManager


cwd = os.getcwd()


def faultyFileDetection(erc_drc_check, faulty_file_check) -> bool:
    #faulty file detection
    
    gitmanager = GitManager(cwd)
    faultyFile = False

    kicad_files_endings = FILE_PARSERS.keys()

    schematic = kicad_files_endings[0]
    pcb = kicad_files_endings[1]
    
    sch_files = [f for f in os.listdir(gitmanager.repo.working_tree_dir) 
                 if os.path.isfile(os.path.join(gitmanager.repo.working_tree_dir, f)) and re.search(f"{schematic}$", f)]
    pcb_files = [f for f in os.listdir(gitmanager.repo.working_tree_dir) 
                 if os.path.isfile(os.path.join(gitmanager.repo.working_tree_dir, f)) and re.search(f"{pcb}$", f)]
    
    if faulty_file_check:
        for file in sch_files:
            args = ["kicad-cli", "sch", "erc", file]

            result = subprocess.run(args, capture_output=True, check=False, text=True)

            if result.stderr:
                print(f"Kicad sch file \"{file}\" is faulty!")
                faultyFile = True
            elif erc_drc_check:
                print(f"ERC check: \n{result.stdout}")
            else:
                print("No faulty Kicad schematic files found!")

        for file in pcb_files:
            args = ["kicad-cli", "pcb", "drc", file]

            result = subprocess.run(args, capture_output=True, check=False, text=True)

            if result.stderr:
                print(f"Kicad PCB file \"{file}\" is faulty!")
                faultyFile = True
            elif erc_drc_check: 
                print(f"DRC check: \n{result.stdout}")
            else:
                print("No faulty KiCad PCB files found!")
            
        return faultyFile


    elif erc_drc_check:
        for file in sch_files:
            args = ["kicad-cli", "sch", "erc", file]

            result = subprocess.run(args, capture_output=True, check=False, text=True)

            print(f"ERC check: \n{result.stdout}")

        for file in pcb_files:
            args = ["kicad-cli", "pcb", "drc", file]

            result = subprocess.run(args, capture_output=True, check=False, text=True)

            print(f"DRC check: \n{result.stdout}")
        
        return 0


    


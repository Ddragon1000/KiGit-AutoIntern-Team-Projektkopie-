import subprocess
import os
import re
from scripts.DiffResRenderer import FaultyFileOutput

from kigit_globals import FILE_PARSERS
from scripts.commands import GitManager


cwd = os.getcwd()


def faultyFileDetection(erc_drc_check, faulty_file_check, faulty_file_output: FaultyFileOutput) -> bool:
    #faulty file detection
    
    gitmanager = GitManager(cwd)
    faultyFile = False

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
                print(f"Kicad sch file \"{file}\" is faulty!")
                faultyFile = True
                file_check = [file, faultyFile, False, None]
                faulty_file_output.add_schematic(file_check)
            elif erc_drc_check:
                print(f"ERC check: \n{result.stdout}")
                faultyFile = False
                file_check = [file, faultyFile, True, result.stdout]
                faulty_file_output.add_schematic(file_check)
            else:
                print("No faulty Kicad schematic files found!")
                faultyFile = False
                file_check = [file, faultyFile, False, None]
                faulty_file_output.add_schematic(file_check)

        for file in pcb_files:
            args = ["kicad-cli", "pcb", "drc", file]

            result = subprocess.run(args, capture_output=True, check=False, text=True)

            if result.stderr:
                print(f"Kicad PCB file \"{file}\" is faulty!")
                faultyFile = True
                file_check = [file, faultyFile, False, None]
                faulty_file_output.add_pcb(file_check)
            elif erc_drc_check: 
                print(f"DRC check: \n{result.stdout}")
                faultyFile = False
                file_check = [file, faultyFile, True, result.stdout]
                faulty_file_output.add_pcb(file_check)
            else:
                print("No faulty KiCad PCB files found!")
                faultyFile = False
                file_check = [file, faultyFile, False, None]
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


    


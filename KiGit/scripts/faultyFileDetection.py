import subprocess
import os
import re

from scripts.commands import GitManager


cwd = os.getcwd()


def faultyFileDetection() -> int:
    #faulty file detection
    
    gitmanager = GitManager(cwd)
    faultyFile = False
    
    sch_files = [f for f in os.listdir(gitmanager.repo.working_tree_dir) 
                 if os.path.isfile(os.path.join(gitmanager.repo.working_tree_dir, f)) and re.search("_sch$", f)]
    pcb_files = [f for f in os.listdir(gitmanager.repo.working_tree_dir) 
                 if os.path.isfile(os.path.join(gitmanager.repo.working_tree_dir, f)) and re.search("_pcb$", f)]
    
    for file in sch_files:
        args = ["kicad-cli", "sch", "erc", file]

        result = subprocess.run(args, capture_output=True, check=False, text=True)

        if result.stderr == "Failed to load schematic\n":
            print(f"Kicad sch file \"{file}\" is faulty!")
            faultyFile = True
        else:
            print(f"ERC check: \n{result.stdout}")

    for file in pcb_files:
        args = ["kicad-cli", "pcb", "drc", file]

        result = subprocess.run(args, capture_output=True, check=False, text=True)

        if result.stderr == "Failed to load board\n":
            print(f"Kicad PCB file \"{file}\" is faulty!")
            faultyFile = True
        else: 
            print(f"DRC check: \n{result.stdout}")
        
    if faultyFile == True:
        return -1
    else:
        return 0
    



class ERC_DRC_Files:
    def __init__(self):
        self.schematic_files : list[list[str, str]] = [] # list of lists that contain the output relevant information: 
                                                                     #[file, faulty, result.stdout for erc_drc_check]
        self.pcb_files : list[list[str, str]] = []

    def add_schematic(self, file_check: list[str, str]):
        #adds a list object of relevant output information of a schematic file check to the schematic list of the class
        self.schematic_files.append(file_check)

    def add_pcb(self, file_check: list[str, str]):
        #adds a list object of relevant output information of a pcb file check to the pcb list of the class
        self.pcb_files.append(file_check)
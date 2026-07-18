import os
import json
import scripts.DiffRes as d
import scripts.BasicChange as bc
from scripts.commands import GitManager
from enum import Enum
from abc import ABC, abstractmethod
from rich.table import Table
from rich.console import Console
cwd = os.getcwd()


class OutputFormat(str, Enum):
    TABLE = "table"
    JSON = "json"
    HTML = "html"

class DiffResRenderer(ABC):
    @abstractmethod
    def render(self, dr : d.DiffRes): 
        pass

class JsonDiffRenderer(DiffResRenderer):
    def render(self, dr : d.DiffRes) -> str:

        summary = {
            "total_changes": len(dr.changes),
            "files": {}
        }

        for components in dr.filterFile():
            filename = components.changes[0].origin

            summary["files"][filename] = {
                "file_changes": len(components.changes),
                "added": len(dr.getAdded()),
                "removed": len(dr.getRemoved()),
                "modified": len(dr.getModified())
            }

        
        return json.dumps({"summary": summary}, indent=2, ensure_ascii=False)
    
    def _serialize_change(self, change : bc.BasicChange) -> dict[str, object]:
        name = change.__class__.__name__
        match name: 
            case "ComponentAdded":
                type = "added"
            case "ComponentRemoved":
                type = "removed"
            case _:
                type = "modified"
        
        return {
            "type": type,
            "element": change.reference
        }
    
    def detailed_render(self, dr: d.DiffRes) -> str:
        files_dict = {}

        for components in dr.filterFile():
            filename = components.changes[0].origin
            file_changes = [
                self._serialize_change(change)
                for change in components.changes
            ]
            
            files_dict[filename] = file_changes
        
        return json.dumps({"files": files_dict}, indent=2, ensure_ascii=False)
           
class HTMLDiffRenderer(DiffResRenderer):

    def __init__(self, s_f):
        self.show_filename = s_f

    def render(self, dr: d.DiffRes) -> str:
        html = "<html>\n<body>\n<h1>KiGit Report</h1>\n"
        html += f"<p><strong>Aenderungen gesamt:</strong> {len(dr.changes)}</p>\n"
        html += "<ul>\n" 

        if not self.show_filename:
            for components in dr.groupByComponent():
                part = components.changes[0].reference
                html += f"  <li><strong>{part}</strong> - Added: {len(components.getAdded())} | Removed: {len(components.getRemoved())} | Modified: {len(components.getModified())}</li>\n"
        
        else:
            for components in dr.filterFile():
                filename = components.changes[0].origin
                for entry in components.groupByComponent():
                    part = entry.changes[0].reference
                    html += f"  <li><strong>{part}</strong> (in {filename}) - Added: {len(entry.getAdded())} | Removed: {len(entry.getRemoved())} | Modified: {len(entry.getModified())}</li>\n"

        html += "</ul>\n</body>\n</html>"
        return html
    
class TableDiffRenderer(DiffResRenderer):

    def __init__(self, s_f):
        self.show_filename = s_f

    def render(self, dr_or_components) -> Table:
            table = Table(title="kigit diff")
            table.add_column("Part", justify="center", style="white")
            table.add_column("Added", justify="center", style="green")
            table.add_column("Removed", justify="center", style="red")
            table.add_column("Modified", justify="center", style="yellow")

            if self.show_filename:
                table.add_column("Filename", justify="center", style="white")

                # Determine if we were given a full DiffRes object or already a list of components
                if hasattr(dr_or_components, 'groupByComponent'):
                    components_iterable = dr_or_components.groupByComponent() if not self.show_filename else dr_or_components.filterFile()
                else:
                    components_iterable = dr_or_components

                if not self.show_filename:
                    for components in components_iterable:
                        table.add_row(str(components.changes[0].reference),
                                      str(len(components.getAdded())),
                                      str(len(components.getRemoved())),
                                      str(len(components.getModified())))
                else:
                    for components in components_iterable:
                        for entry in components.groupByComponent(): #Q: why is this here, is it not the same to the one above?
                            table.add_row(str(entry.changes[0].reference),
                                          str(len(components.getAdded())),
                                          str(len(components.getRemoved())),
                                          str(len(components.getModified())),
                                          str(components.changes[0].origin))
                return table


    #same as render but allows for pagination at the cost of a hardcoded max table size
    def render_paginated(self, dr: d.DiffRes, max_size: int = 23):
        from rich.console import Console
        console = Console()
        #problem with doing it in renderdiff is that I could not call on "show_filename" which causes one or the other
        #to return with 'None', to fix this the code must happen where we get the info for show_filename.
        #system to dynamically change filetype was with assistance
        if self.show_filename:
            source_list = list(dr.filterFile())
        else:
            source_list = list(dr.groupByComponent())

        # for page display
        total_pages = (len(source_list) + (max_size - 1)) // max_size
        current_page = 0

        while True:
            console.clear()

            # data to create the chunk
            start = current_page * max_size
            end = start + max_size
            chunk = source_list[start:end]


            page_table = Table(title=f"kigit diff (Page {current_page + 1}/{total_pages})")
            page_table.add_column("Part", justify="center", style="white")
            page_table.add_column("Added", justify="center", style="green")
            page_table.add_column("Removed", justify="center", style="red")
            page_table.add_column("Modified", justify="center", style="yellow")

            if self.show_filename:
                page_table.add_column("Filename", justify="center", style="white")

            if not self.show_filename:
                for components in chunk:
                    page_table.add_row(
                        str(components.changes[0].reference),
                        str(len(components.getAdded())),
                        str(len(components.getRemoved())),
                        str(len(components.getModified()))
                    )
            else:
                for components in chunk:
                    for entry in components.groupByComponent():
                        page_table.add_row(
                            str(entry.changes[0].reference),
                            str(len(components.getAdded())),
                            str(len(components.getRemoved())),
                            str(len(components.getModified())),
                            str(components.changes[0].origin)
                        )

            # print chunk
            console.print(page_table)

            # page select via CL
            if not self.show_filename:
                #the paging looks bad on an obviously short print
                break

            print(f"\n[N]ext Page  |  [P]revious Page  |  [Q]uit")
            user_input = input("Choose an option: ").strip().lower()

            if user_input == 'n' and current_page < total_pages - 1:
                current_page += 1
            elif user_input == 'p' and current_page > 0:
                current_page -= 1
            elif user_input == 'q':
                break


def render_diff(dr : d.DiffRes, renderer : DiffResRenderer):
    output = renderer.render(dr)

    if isinstance(renderer,HTMLDiffRenderer):

        import webbrowser
        import os

        filename = "kigit_report.html"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(output)

        webbrowser.open("file://" + os.path.realpath(filename))

    elif isinstance(renderer, JsonDiffRenderer):
        print(output)
        
        from rich.prompt import Confirm
        if Confirm.ask("Do you want to download a detailed JSON-file?"):
            detailed = renderer.detailed_render(dr)

            filename = "kigit_diff.json"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(detailed)
            
            print(f"Downloaded succesfully under current working directory with the name: {filename}")

    elif isinstance(renderer, TableDiffRenderer):
        renderer.render_paginated(dr)


def call_status():
    """Shows the KiGit status"""
    console = Console()
    gitmanager = GitManager(cwd)

    gitstatus = gitmanager.status()

    if gitstatus:
        status_array = gitstatus.splitlines()

        table = Table(title="kigit status")
        table.add_column("Staging Area", justify="center")
        table.add_column("Working Directory", justify="center")
        table.add_column("File", justify="center")

        for line in status_array:
            table.add_row(str(line[0]),
                          str(line[1]),
                          str(line[2:]))

        console.print(table)
    else:
        print("No current updates at the moment.")



class FaultyFileOutput:

    def __init__(self):
        self.schematic_files : list[list[str, bool, str]] = [] # list of lists that contain the output relevant information: 
                                                                     #[file, faulty, result.stdout for erc_drc_check]
        self.pcb_files : list[list[str, bool, str]] = []

    def add_schematic(self, file_check: list[str, bool, str]):
        #adds a list object of relevant output information of a schematic file check to the schematic list of the class
        self.schematic_files.append(file_check)

    def add_pcb(self, file_check: list[str, bool, str]):
        #adds a list object of relevant output information of a pcb file check to the pcb list of the class
        self.pcb_files.append(file_check)

    def output(self):
        #iterates through the schematic file list to output every file check
        for file in self.schematic_files:
            file_name = file[0]
            faulty = file[1]
            erc_output = file[2]

            if faulty:
                print(f"Kicad sch file \"{file_name}\" is faulty!")
            else:
                print(f"ERC check: {erc_output}")


        for file in self.pcb_files: 
            #iterates through the pcb file list to output every file check
            file_name = file[0]
            faulty = file[1]
            drc_output = file[2]
            
            if faulty:
                print(f"Kicad pcb file \"{file_name}\" is faulty!")
            else:
                print(f"DRC check: {drc_output}")





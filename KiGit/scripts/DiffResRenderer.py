import json
import scripts.DiffRes as d
import scripts.BasicChange as bc
from enum import Enum
from abc import ABC, abstractmethod
from rich.table import Table


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

    def render(self, dr: d.DiffRes) -> Table: 
            table = Table(title="kigit diff")
            table.add_column("Part", justify="center", style="white")
            table.add_column("Added", justify="center", style="green")
            table.add_column("Removed", justify="center", style="red")
            table.add_column("Modified", justify="center", style="yellow")

            if self.show_filename:
                table.add_column("Filename", justify="center", style="white")
    
            if not self.show_filename:
                for components in dr.groupByComponent():
                    table.add_row(str(components.changes[0].reference),
                        str(len(components.getAdded())),
                        str(len(components.getRemoved())),
                        str(len(components.getModified())))
            else:
                for components in dr.filterFile():
                    for entry in components.groupByComponent():
                        table.add_row(str(entry.changes[0].reference),
                                    str(len(entry.getAdded())),
                                    str(len(entry.getRemoved())),
                                    str(len(entry.getModified())),
                                    str(entry.changes[0].origin))
            return table
        
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
        from rich.console import Console
        Console().print(output)

 
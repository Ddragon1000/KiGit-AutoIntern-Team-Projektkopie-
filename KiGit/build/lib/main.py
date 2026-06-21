import typer
import os
import re
from rich.console import Console
from rich.table import Table
from parser.diff_parser import KiCadDiffParser
from scripts.commands import GitManager
from typing import List
from typing import Annotated, Optional
import scripts.BasicChange as bc


app = typer.Typer()
console = Console()
cwd = os.getcwd()


@app.command()
def diff(
        args: Annotated[Optional[List[str]], typer.Argument(help="commit file or file or commit")] = None,
        show_filename: bool = typer.Option(False, help="Shows corresponding Filename in result"),
        detail: str = typer.Option("", "--detail", help="Filters detail screen"),
        debug: bool = typer.Option(False, help="enables Debug options")
        ):
    """Shows the KiGit diff"""

    #default values
    commit = "HEAD"
    file = None
    
    if args:
        if len(args) == 1:
            val = args[0]
            if re.search(r"\.kicad_.*$", val) or "/" in val:
                file = val
            else:
                commit = val
                file = None
        elif len(args) == 2:
            commit = args[0]
            file = args[1]

    #object creation
    gitmanager = GitManager(cwd)

    parser = KiCadDiffParser()
    
    diff_result = gitmanager.diff(commit, file)

    if isinstance(diff_result, str):
        print(f"[ERROR] Git: {diff_result}")
        raise typer.Exit(1)
    else:
        stats = parser.parse(diff_result, working_tree_dir=gitmanager.repo.working_tree_dir)

    if stats.isEmpty():
        typer.echo("No KiCad file changes detected")
        raise typer.Exit(1)

    if debug:
        print(f"[DEBUG] {stats}")

    if not detail:
        table = Table(title="kigit diff")
        table.add_column("Part", justify="center", style="white")
        table.add_column("Added", justify="center", style="green")
        table.add_column("Removed", justify="center", style="red")
        table.add_column("Modified", justify="center", style="yellow")
        if show_filename:
            table.add_column("Filename", justify="center", style="white")
    
        if not show_filename:
            for components in stats.groupByComponent():
                table.add_row(str(components.changes[0].reference),
                              str(len(components.getAdded())),
                              str(len(components.getRemoved())),
                              str(len(components.getModified())))
        else:
            for components in stats.filterFile():
                for entry in components.groupByComponent():
                    table.add_row(str(entry.changes[0].reference),
                                  str(len(entry.getAdded())),
                                  str(len(entry.getRemoved())),
                                  str(len(entry.getModified())),
                                  str(entry.changes[0].origin))


        console.print(table)
    else:
        table = Table(title="KiGit Diff Detail Screen")
        """
        Format: xy XY
        """
        table.add_column("Part", justify="center")
        match detail.lower():
            case "modified":
                table.add_column("Old Position", justify="center")
                table.add_column("New Position", justify="center")
                modified = stats.getModified()
                for entry in modified:
                    if isinstance(entry, bc.ComponentMoved):
                        table.add_row(str(entry.reference),
                                      str(entry.coordinates[0]),
                                      str(entry.coordinates[1]))
        console.print(table)

@app.command()
def status():
    """Shows the KiGit status"""

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

#_ wird zu - in CLI
@app.command()
def quick_status():
    """shows dirtyness of git repo"""
    gitmanager = GitManager(cwd)
    status = gitmanager.get_change_status()
    print("There have been changes" if status else "No changes at the moment")

if __name__ == "__main__":
    app()

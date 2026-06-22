import typer
import os
import re
from rich.console import Console
from rich.table import Table
from parser.diff_parser import KiCadDiffParser
from scripts.commands import GitManager
from typing import List
from typing import Annotated, Optional
import scripts.DiffResRenderer as r


app = typer.Typer()
console = Console()
cwd = os.getcwd()


@app.command()
def diff(
        args: Annotated[Optional[List[str]], typer.Argument(help="commit file or file or commit")] = None,
        show_filename: bool = typer.Option(False, help="Shows corresponding Filename in result"),
        debug: bool = typer.Option(False, help="enables Debug options"),
        output: r.OutputFormat = typer.Option(r.OutputFormat.TABLE, "--output", "-o", help="Output Format")
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
    
    stats = parser.parse(gitmanager.diff(commit, file))

    if stats.isEmpty():
        typer.echo("No KiCad file changes detected")
        raise typer.Exit(1)

    if debug:
        print(f"[DEBUG] {stats}")

    if output == r.OutputFormat.TABLE:
        r.render_diff(stats, r.TableDiffRenderer(show_filename))
    elif output == r.OutputFormat.JSON:
        r.render_diff(stats, r.JsonDiffRenderer())
    elif output == r.OutputFormat.HTML:
        r.render_diff(stats, r.HTMLDiffRenderer(show_filename))
       

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

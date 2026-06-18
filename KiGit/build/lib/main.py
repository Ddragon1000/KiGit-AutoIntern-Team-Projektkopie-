import typer
import os
import re
from rich.console import Console
from rich.table import Table
from parser.diff_parser import KiCadDiffParser
from scripts.commands import GitManager
from typing import List
from typing import Annotated, Optional


app = typer.Typer(
    name="KiGit",
    help=(
		"A CLI Tool for a better version Control for KiCad with Git\n\n"
        "This Tool is intendet for the use inside a Repository holding KiCad project(s)\n\n"
        "Use [italic]kigit COMMAND --help[/italic] for details\n\n"
        "[underline]Common Workflow:[/underline] \n\n"
        "Start with [italic]kigit quick-status[/italic] to know if there are current changes\n\n"
        "Optionally continue using [italic]kigit status[/italic] to know where the changes are\n\n"
        "Lastly continue using [italic]kigit diff[/italic] for a short summary of what changed in files\n\n"
        ),
    no_args_is_help=True,
    rich_markup_mode="rich",
    #epilog=""
)
console = Console()
cwd = os.getcwd()


@app.command()
def diff(
        args: Annotated[Optional[List[str]], typer.Argument(help="commit, file, branches or tags")] = None,
        show_filename: bool = typer.Option(False, help="breaks down statistic for each file including filename"),
        debug: bool = typer.Option(False, help="Shows debug messages")
        ):
    """Show changes between commits, commit and working tree and more for KiCad files"""

    #default values
    commit = ["HEAD", None]
    file = None
    
    if args:
        if len(args) == 1:
            val = args[0]
            if re.search(r"\.kicad_.*$", val) or "/" in val:
                file = val
            else:
                commit[0] = val
                file = None
        elif len(args) == 2:
            val = args[1]
            if re.search(r"\.kicad_.*$", val) or "/" in val:
                commit[0] = args[0]
                file = val
            else:
                commit[0] = args[0]
                commit[1] = args[1]

    #object creation
    gitmanager = GitManager(cwd)

    parser = KiCadDiffParser()
    
    stats = parser.parse(gitmanager.diff(commit[0], commit[1], file))

    if not stats:
        typer.echo("No KiCad-Files found in Diff")
        raise typer.Exit(1)

    if debug:
        print(f"[DEBUG] {stats}")

    table = Table(title="kigit diff")
    table.add_column("Part", justify="center", style="white")
    table.add_column("Added", justify="center", style="green")
    table.add_column("Removed", justify="center", style="red")
    table.add_column("Modified", justify="center", style="yellow")
    if show_filename:
        table.add_column("Filename", justify="center", style="white")

    if debug:
        print(stats[0].filetype)
    
    for entry in stats:
        if show_filename:
            table.add_row(f"{entry.filetype}",
                        str(entry.result.added),
                        str(entry.result.removed),
                        str(entry.result.changed),
                        str(entry.filename))
        else:
            table.add_row(f"{entry.filetype}",
                        str(entry.result.added),
                        str(entry.result.removed),
                        str(entry.result.changed))
    console.print(table)

@app.command()
def status():
    """Show the working tree status of KiCad files"""

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
    """Show a quick message of the status of your KiCad files in your Repository"""
    gitmanager = GitManager(cwd)
    status = gitmanager.get_change_status()
    print("There are current changes" if status else "No changes at the moment")

if __name__ == "__main__":
    app()

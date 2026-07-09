import typer
import os
import re
import scripts.DiffResRenderer as renderer
import scripts.BasicChange as bc
import subprocess
from rich.console import Console
from rich.table import Table
from parser.diff_parser import KiCadDiffParser
from scripts.commands import GitManager
from typing import Annotated

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
#`os.getcwd()` should be replaced by `Path.cwd()`
cwd = os.getcwd()

#Boolean-typed positional argument in function definition debug:
#Boolean positional value in function call typer.Option(False, ...)
#same with show_filename: ... (False, ...)
@app.command()
def diff(
        args: Annotated[list[str] | None, typer.Argument(help="commit file or file or commit")] = None,
        show_filename: bool = typer.Option(False, help="Shows corresponding Filename in result"),
        output: renderer.OutputFormat = typer.Option(renderer.OutputFormat.TABLE, "--output", "-o", help="Output Format"),
        detail: str = typer.Option("", "--detail", help="Filters detail screen"),
        debug: bool = typer.Option(False, help="enables Debug options")
        ):
    """Show changes between commits, commit and working tree and more for KiCad files"""

    #default values
    commit = ["HEAD", None]
    file = None

    if args:
        #remove magic values ==1 and ==2 ?
        if len(args) == 1:
            val = args[0]
            if re.search(r"\.kicad_.*$", val) or "/" in val:
                file = val
            else:
                commit[0] = val
        elif len(args) == 2:
            val = args[1]
            if re.search(r"\.kicad_.*$", val) or "/" in val:
                commit[0] = args[0]
                file = val
            else:
                commit[0] = args[0]
                commit[1] = args[1]
        elif len(args) == 3:
            commit[0] = args[0]
            commit[1] = args[1]
            file = args[2]

    #object creation
    gitmanager = GitManager(cwd)

    parser = KiCadDiffParser()

    sch_files = [f for f in os.listdir(gitmanager.repo.working_tree_dir) 
                 if os.path.isfile(os.path.join(gitmanager.repo.working_tree_dir, f)) and re.search("_sch$", f)]
    pcb_files = [f for f in os.listdir(gitmanager.repo.working_tree_dir) 
                 if os.path.isfile(os.path.join(gitmanager.repo.working_tree_dir, f)) and re.search("_pcb$", f)]
    
    faultyFileDetection(sch_files, pcb_files)
    
    diff_result = gitmanager.diff(commit[0], commit[1], file)

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

    if output == renderer.OutputFormat.TABLE:
        renderer.render_diff(stats, renderer.TableDiffRenderer(show_filename))
    elif output == renderer.OutputFormat.JSON:
        renderer.render_diff(stats, renderer.JsonDiffRenderer())
    elif output == renderer.OutputFormat.HTML:
        renderer.render_diff(stats, renderer.HTMLDiffRenderer(show_filename))
       

@app.command()
def status():
    renderer.call_status()
#_ wird zu - in CLI
@app.command()
def quick_status():
    """Show a quick message of the status of your KiCad files in your Repository"""
    gitmanager = GitManager(cwd)
    status = gitmanager.get_change_status()
    print("There are current changes" if status else "No changes at the moment")


def faultyFileDetection(sch_files, pcb_files):
    #faulty file detection
    for file in sch_files:
        args = ["kicad-cli", "sch", "erc", file]

        result = subprocess.run(args, capture_output=True, check=True, text=True)

        if result.stdout == "Failed to load schematic":
            print("Kicad sch file {file} is faulty!")

    for file in pcb_files:
        args = ["kicad-cli", "pcb", "drc", file]

        result = subprocess.run(args, capture_output=True, check=True, text=True)

        if result.stdout == "Failed to load schematic":
            print("Kicad PCB file {file} is faulty!")




if __name__ == "__main__":
    app()


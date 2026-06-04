import typer
import os
from lark.exceptions import UnexpectedEOF, UnexpectedInput
from rich.console import Console
from rich.table import Table
from scripts.Git_Commands import gitDiff
from parser.diff_parser import KiCadDiffParser
from scripts.commands import GitManager

app = typer.Typer()
console = Console()
TMP_DIR = os.path.join(os.path.expanduser("~"), ".kigit", "tmp")
cwd = os.getcwd()


@app.command()
def diff(
        file: str = typer.Argument(None, help="Path to KiCad File"),
        commit: str = typer.Argument("HEAD", help="Commit-Hash (optional)"),
        debug: bool = typer.Option(False, help="enables Debug options")
        ):
    """Shows the KiGit diff"""
    gitDiff(file, commit, debug)

    pure_name = os.path.basename(file).replace(".", "_")
    path = os.path.join(TMP_DIR, f"tmp_{pure_name}.txt")
    
    gitmanager = GitManager(cwd)

    parser = KiCadDiffParser()

    if debug:
        print(f"[DEBUG] suche datei: {path}")
    
    stats = parser.parse(gitmanager.diff(commit, file))

    if not stats:
        typer.echo("No KiCad-Files found in Diff")
        raise typer.Exit(1)

    if debug:
        print(f"[DEBUG] {stats}")

    table = Table(title="kigit diff")
    table.add_column("changed", justify="center", style="white")
    table.add_column("added", justify="center", style="green")
    table.add_column("removed", justify="center", style="red")
    table.add_column("modified", justify="center", style="yellow")

    table.add_row(f"{stats[0].filetype}",
                  str(stats[0].result.added),
                  str(stats[0].result.removed),
                  str(stats[0].result.changed))
    console.print(table)

@app.command()
def status():
    """Shows the KiGit status"""
    #änderungen ja/nein
    # plan:
    # call git command (from git control script)
    # parse git output into parser
    # print parsed text out
    # Idea: git status says if valid repo
    # but what if valid repo is not a KiCad Project?
    # --> maybe add functionality of detecting KiCad Projects
    pass


if __name__ == "__main__":
    app()

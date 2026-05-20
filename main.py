import typer
import os
from lark.exceptions import UnexpectedEOF, UnexpectedInput
from parser.parser import count_changes
from parser.parser import DiffStats
from rich.console import Console
from rich.table import Table
from scripts.Git_Commands import gitDiff
from parser.new_parser import KiCadDiffParser

app = typer.Typer()
console = Console()
TMP_DIR = os.path.join(os.path.expanduser("~"), ".kigit", "tmp")


@app.command()
def diff(
        file: str = typer.Argument(..., help="Path to KiCad File"),
        commit: str = typer.Argument(None, help="Commit-Hash (optional)"),
        debug: bool = typer.Option(False, help="enables Debug options")
        ):
    """Shows the KiGit diff"""
    gitDiff(file, commit, debug)
    pure_name = os.path.basename(file).replace(".", "_")
    path = os.path.join(TMP_DIR, f"tmp_{pure_name}.txt")
    parser = KiCadDiffParser(str(path))
    if debug:
        print(f"[DEBUG] suche datei: {path}")
    
    stats = parser.parse(str(path))

    if not stats:
        typer.echo("No KiCad-Files found in Diff")
        raise typer.Exit(1)

    if debug:
        print(f"[DEBUG] {stats}")

    table = Table(title="Difference in Wires and Tracks")
    table.add_column("changed", justify="center", style="white")
    table.add_column("removed", justify="center", style="red")
    table.add_column("added", justify="center", style="green")
    table.add_column("modified", justify="center", style="green")

    table.add_row("wires",
                  str(stats.wire_removed),
                  str(stats.wire_added),
                  str(stats.wire_modified))
    table.add_row("segments",
                  str(stats.track_removed),
                  str(stats.track_added),
                  str(stats.track_modified))
    console.print(table)


@app.command()
def status():
    """Shows the KiGit status"""
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

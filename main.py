import typer
from parser.parser import count_changes
from pathlib import Path
from rich.console import Console
from rich.table import Table

app = typer.Typer()
console = Console()
project_root = Path(__file__).parent

@app.command()
def diff(path = (project_root / "tmp" / "tmp.txt")):
    """Shows the KiGit diff"""
    stats = count_changes(str(path))
    table = Table(title="Difference in Wires and Tracks")
    table.add_column("changed", justify="center", style="white")
    table.add_column("removed", justify="center", style="red")
    table.add_column("added", justify="center", style="green")

    table.add_row("wires", str(stats.wire_removed), str(stats.wire_added))
    table.add_row("segments", str(stats.track_removed), str(stats.track_added))
    #plan:
    #call git command (from git control script)
    #parse git ouput into parser
    #print parsed text out
    console.print(table)

@app.command()
def status():
    """Shows the KiGit status"""
    #plan:
    #call git command (from git control script)
    #parse git output into parser
    #print parsed text out
    #Idea: git status says if valid repo
    #but what if valid repo is not a KiCad Project?
    #--> maybe add functionality of detecting KiCad Projects
    pass

if __name__ == "__main__":
    app()

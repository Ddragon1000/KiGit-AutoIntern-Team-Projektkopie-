import typer
from parser.parser import count_changes
from pathlib import Path

app = typer.Typer()


@app.command()
def diff():
    """Shows the KiGit diff"""
    project_root = Path(__file__).parent
    stats = count_changes(str(project_root / "tmp" / "tmp.txt"))
    #plan:
    #call git command (from git control script)
    #parse git ouput into parser
    #print parsed text out
    print(stats)

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

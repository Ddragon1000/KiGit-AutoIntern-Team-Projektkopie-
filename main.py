import typer

app = typer.Typer()


@app.command()
def diff():
    """Shows the KiGit diff"""
    #plan:
    #call git command (from git control script)
    #parse git ouput into parser
    #print parsed text out
    pass

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

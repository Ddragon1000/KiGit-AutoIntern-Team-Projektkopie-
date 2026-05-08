import typer

app = typer.Typer()


@app.command()
def diff():
    """Shows the KiGit diff"""
    pass

@app.command()
def status():
    """Shows the KiGit status"""
    pass

if __name__ == "__main__":
    app()

import logging
import typer
import os
import re
import scripts.DiffResRenderer as renderer
import scripts.BasicChange as bc
from rich.console import Console
from rich.table import Table
from parser.diff_parser import KiCadDiffParser
from scripts.commands import GitManager
from scripts.logging_config import setup_logging
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

logger = logging.getLogger(__name__)



def version_callback(value: bool):
    import importlib.metadata
    if value:
        version = importlib.metadata.version("KiGit_AutoIntern-3")
        
        typer.echo(f"Kigit Version: {version} \n"
                   "Developers: Dennis Piotrowski, Jannick Tim Medda, Marcel Wiemann, Ismail Koc, Daniel Quayes, Adrian Sturm")
        raise typer.Exit()


@app.callback()
def main(
    verbose: Annotated[
        int,
        typer.Option(
            "--verbose", "-v",
            count = True,
            help = "Verbosity, -v -v for more details"
        )
    ] = 0,
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            callback= version_callback,
            is_eager= True,
            help= "Developer and Version of Kigit"
        ),
    ] = False,
): 
    setup_logging(verbose)
    logger.debug(f"logging configured with verbosity level {verbose}")


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

    logger.info("starting \"diff\"-command")
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

    logger.debug(f"parameters: commit={commit}, file={file}")

    #object creation
    gitmanager = GitManager(cwd)
    logger.debug(f"initialized Gitmanager for: {cwd}")

    parser = KiCadDiffParser()
    
    logger.debug(f"calling gitmanger.diff({commit[0]}), {commit[1]}, {file}")
    diff_result = gitmanager.diff(commit[0], commit[1], file)

    if isinstance(diff_result, str):
        print(f"[ERROR] Git: {diff_result}")
        raise typer.Exit(1)
    else:
        logger.info("Parsing git-diff results")
        stats = parser.parse(diff_result, working_tree_dir=gitmanager.repo.working_tree_dir)

    if stats.isEmpty():
        typer.echo("No KiCad file changes detected")
        raise typer.Exit(1)

    if debug:
        print(f"[DEBUG] {stats}")

    logger.info(f"Rendering results in format: {output.value}")

    if output == renderer.OutputFormat.TABLE:
        renderer.render_diff(stats, renderer.TableDiffRenderer(show_filename))
    elif output == renderer.OutputFormat.JSON:
        renderer.render_diff(stats, renderer.JsonDiffRenderer())
    elif output == renderer.OutputFormat.HTML:
        renderer.render_diff(stats, renderer.HTMLDiffRenderer(show_filename))
       

@app.command()
def status():
    logger.info("starting \"status\"-command")
    renderer.call_status()
#_ wird zu - in CLI
@app.command()
def quick_status():
    """Show a quick message of the status of your KiCad files in your Repository"""
    logger.info("starting \"quick_status\"-command")
    gitmanager = GitManager(cwd)
    status = gitmanager.get_change_status()
    print("There are current changes" if status else "No changes at the moment")

if __name__ == "__main__":
    app()

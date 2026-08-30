"""
MIT License

Copyright (c) Jannick Tim Medda, Dennis Piotrowski, Marcel Wiemann, Ismail Koc, Daniel Quayes, Adrian Sturm

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import logging
import psutil
import typer
import os, sys
import re
import scripts.DiffResRenderer as renderer
import scripts.BasicChange as bc
from rich.console import Console
from rich.table import Table
from parser.diff_parser import KiCadDiffParser
from scripts.commands import GitManager
from scripts.logging_config import setup_logging
from typing import Annotated
from scripts.faultyFileDetection import faultyFileDetection, erc_drc_func
import scripts.mkdocs as mk

Valid_details = {"all","start","end","width","layer","net","pts","stroke","modified"}

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


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
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
    docs: Annotated[
        bool,
        typer.Option(
            "--docs",
            callback=mk.docs_callback,
            is_eager=True,
            help="Opens webbrowser with KiGit documentation page",
        ),
        ] = False,
): 
    setup_logging(verbose)
    logger.debug(f"logging configured with verbosity level {verbose}")

    if ctx.invoked_subcommand is None and not docs:
        typer.echo(ctx.get_help())
        raise typer.Exit()


def isPowerShell():
    process_id = os.getpid() #get ID from KiGit-Process
    current_process = psutil.Process(process_id) #Object that has information about Process

    for parent in current_process.parents(): #goes through object to find correct parent
        parent_name = parent.name().lower()
        if parent_name == "powershell.exe" or parent_name == "pwsh.exe":
            return True 
    return False

#Boolean-typed positional argument in function definition debug:
#Boolean positional value in function call typer.Option(False, ...)
#same with show_filename: ... (False, ...)
@app.command()
def diff(
        args: Annotated[list[str] | None, typer.Argument(help="commit file or file or commit")] = None,
        show_filename: bool = typer.Option(False, help="Shows corresponding Filename in result"),
        output: renderer.OutputFormat = typer.Option(renderer.OutputFormat.TABLE, "--output", "-o", help="Output Format"),
        detail: str = typer.Option("none","--detail",help="Show all details or only a specific parameter."),
        debug: bool = typer.Option(False, help="enables Debug options"),
        docs: bool = typer.Option(
            False,
            "--docs",
            callback=mk.diff_docs_callback,
            is_eager=True,
            help="opens webbrowser with mkdocs page for diff command",
            )
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

    # Validate the --detail input
    requested = [] if detail == "none" else [d.strip() for d in detail.split(",")]
    valid = []
    invalid = []
    for item in requested:
        if item in Valid_details:
            valid.append(item)
        else:
            invalid.append(item)
    # Rebuild the detail string so we have only the valid parameters.
    detail = ",".join(valid) if valid else "none"

    logger.debug(f"parameters: commit={commit}, file={file}")

    #object creation
    gitmanager = GitManager(cwd)
    logger.debug(f"initialized Gitmanager for: {cwd}")

    parser = KiCadDiffParser()


    faulty_output = renderer.FaultyOutput()
    

    if faulty_file_check or erc_drc:
        ffresult = faultyFileDetection()

        if ffresult:
            faulty_output.faulty_file_output()
            raise typer.Exit(1)


    logger.debug(f"calling gitmanger.diff({commit[0]}), {commit[1]}, {file}")
    diff_result = gitmanager.diff(commit[0], commit[1], file)

    if isinstance(diff_result, str):
        print(f"[ERROR] Git: {diff_result}")
        raise typer.Exit(1)
    else:
        try:
            stats = parser.parse(diff_result, working_tree_dir=gitmanager.repo.working_tree_dir)
        except:
            print("Something went wrong with the parsing. Check if faulty files exist.")
            raise typer.Exit(1)
        logger.info("Parsing git-diff results")
        stats = parser.parse(diff_result, working_tree_dir=gitmanager.repo.working_tree_dir)

    if stats.isEmpty():
        typer.echo("No KiCad file changes detected")
        raise typer.Exit(1)



    if erc_drc:
        erc_drc_faulty = False
        erc_drc_output = renderer.ERC_DRC_Output()
        erc_drc_faulty = erc_drc_func(erc_drc_output, stats, output)
        erc_drc_output.output()
        if erc_drc_faulty:
            faulty_output.faulty_erc_drc_output()
            raise typer.Exit(1)

    if debug:
        print(f"[DEBUG] {stats}")

    logger.info(f"Rendering results in format: {output.value}")

    if output == renderer.OutputFormat.TABLE:
        renderer.render_diff(stats, renderer.TableDiffRenderer(show_filename,detail))
    elif output == renderer.OutputFormat.JSON:
        renderer.render_diff(stats, renderer.JsonDiffRenderer(detail))
        if (isPowerShell()):
            if not sys.stdout.isatty(): #checks if output was redirected to a file
                sys.stderr.write(
                    "\n[KiGit Warning] For Json Output\n"
                    "If you just redirected this output to a file using '>', Windows might force a UTF-16 BOM.\n"
                    "For a clean UTF-8 file, use: kigit diff -o json | Out-File -Encoding utf8 filename.json\n\n"
            )
    elif output == renderer.OutputFormat.HTML:
        renderer.render_diff(stats, renderer.HTMLDiffRenderer(show_filename,detail))

    if invalid:
        print(
            f"\nWarning: The following detail parameter(s) are not supported and were ignored: "
            f"{', '.join(invalid)}"
        )

        if detail == "none":
            print(
                "No valid detail parameters were specified, therefore no parameter details were displayed."
            )

@app.command()
def status(docs: bool = typer.Option(
    False,
    "--docs",
    callback=mk.status_docs_callback,
    is_eager=True,
    help="opens webbrowser with mkdocs page for status command")
    ):
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


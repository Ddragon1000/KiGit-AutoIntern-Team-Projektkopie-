import logging

from rich.console import Console
from rich.logging import RichHandler

log_console = Console(stderr=True)

def setup_logging(verbosity: int):
    """
    Mapping:
        0 (kein -v) -> WARNING 
        1 (-v) -> INFO 
        >2 (-vv) -> DEBUG
    """

    level = {0: logging.WARNING, 1:logging.INFO}.get(verbosity, logging.DEBUG)

    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[
            RichHandler(
                console=log_console,
                show_time=verbosity > 0,
                show_path=verbosity >=2,
                markup=True,
                rich_tracebacks=True
            )
        ],
        force=True
    )
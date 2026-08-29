import webbrowser
import typer
from kigit_globals import docs

def open_docs(path: str = ""):
	"""Opens Browser and ends Typer"""
	if path == "":
		path = docs.index
	webbrowser.open(path)
	raise typer.Exit()

def docs_callback(value: bool):
	"""Callback for kigit --docs (mainpage)"""
	if value:
		open_docs()

def diff_docs_callback(value: bool):
	"""Callback for kigit diff --docs"""
	if value:
		open_docs(docs.cmd.diff)

def status_docs_callback(value: bool):
	"""Callback for kigit status --docs"""
	if value:
		open_docs(docs.cmd.status)


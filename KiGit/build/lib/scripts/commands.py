from git import Repo, InvalidGitRepositoryError, NoSuchPathError, DiffIndex
from pathlib import Path

#File `AutoIntern-3\KiGit\scripts\commands.py` is part of an implicit namespace package. Add an `__init__.py`
#Missing docstring in public module

class GitManager:

	"""Used for seemless connection between KiGit and the current Git Repository"""

	def __init__(self, path: str) -> None:
		"""Init the Repository and catch errors if path is invalid"""
		try:
			self.repo = Repo(path, search_parent_directories=True)
		except (InvalidGitRepositoryError, NoSuchPathError) as e:
			raise ValueError(f"Invalid Git-Repository under path: {path}") from e

	def get_change_status(self) -> bool:
		"""Returns True, if there are unsaved changes (incl. untracked files)"""
		
		return self.repo.is_dirty(untracked_files=True) == True 
	
	def diff(self, commit1: str = "HEAD", commit2: str | None = None, file: str | None = None) -> "DiffIndex | str":
		"""Generates a diff"""

		path_filter = (Path(file)) if file else None

		
		try:
			return self.repo.commit(commit1).diff(other=commit2, paths=path_filter)
		except Exception as e:
			#Do not catch blind exception: `Exception`
			return f"[ERROR] generating diff: {e}"


	def status(self):
		"""Returns a short status"""
		try:
			return self.repo.git.status("-s")
		except Exception as e:
			return f"[ERROR] generating status: {e}"

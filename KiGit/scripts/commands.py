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
import os
from git import Repo, InvalidGitRepositoryError, NoSuchPathError, DiffIndex
from pathlib import Path

#File `AutoIntern-3\KiGit\scripts\commands.py` is part of an implicit namespace package. Add an `__init__.py`
#Missing docstring in public module

class GitManager:

	"""Used for seamless connection between KiGit and the current Git Repository"""

	def __init__(self, path: str) -> None:
		"""Init the Repository and catch errors if path is invalid"""
		try:
			self.repo = Repo(path, search_parent_directories=True)
		except (InvalidGitRepositoryError, NoSuchPathError) as e:
			#Exception must not use an f-string literal, assign to variable first
			raise ValueError(f"Invalid Git-Repository under path: {path}") from e

	def get_change_status(self) -> bool:
		"""Returns True, if there are unsaved changes (incl. untracked files)"""
		#Avoid equality comparisons to `True`; use `self.repo.is_dirty(untracked_files=True):` for truth checks
		#or maybe something like isTrue()?
		return self.repo.is_dirty(untracked_files=True) == True 
	
	def diff(self, commit1: str = "HEAD", commit2: str | None = None, file: str | None = None) -> "DiffIndex | str":
		"""Generates a diff"""

		path_filter = (Path(file)) if file else None

		try:
			return self.repo.commit(commit1).diff(other=commit2, paths=path_filter)
		except Exception as e:
			#Do not catch blind exception: `Exception`
			return f"[ERROR] generating diff: {e}"

	def status(self) -> str:
		"""Returns a short status"""
		try:
			repo_root =  self.repo.working_tree_dir
			allow_list_path = os.path.join(repo_root,".kigitallow")
			allowed_paths = []
			if os.path.exists(allow_list_path):
				with open(allow_list_path, "r", encoding="utf-8") as f:
					allowed_paths = [s for line in f if (s := line.strip()) and not s.startswith("#")]
			
			if allowed_paths:
				return self.repo.git.status("-s", *allowed_paths)
			return self.repo.git.status("-s")
		except Exception as e:
			#Do not catch blind exception: `Exception`
			return f"[ERROR] generating status: {e}"

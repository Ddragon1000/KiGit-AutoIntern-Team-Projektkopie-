from git import Repo, InvalidGitRepositoryError, NoSuchPathError

class GitManager:
	"""Used for seemless connection between KiGit and the current Git Repository"""
	def __init__(self, path: str):
		"""Init the Repository and catch errors if path is invalid"""
		try:
			self.repo = Repo(path, search_parent_directories=True)
		except (InvalidGitRepositoryError, NoSuchPathError) as e:
			raise ValueError(f"Invalid Git-Repository under path: {path}") from e

	def get_change_status(self) -> bool:
		"""Returns True, if there are unsaved changes (incl. untracked files)"""
		
		return self.repo.is_dirty(untracked_files=True) == True 
	
	def diff(self, commit1: str = "HEAD", commit2: str | None = None, file: str | None = None) -> str:
		"""Generates a diff"""
		args = [commit1]
		if commit2:
			args.append(commit2)
		if file:
			args.extend(["--", file])

		try:
			return self.repo.git.diff(*args)
		except Exception as e:
			return f"[ERROR] generating diff: {e}"

	def status(self):
		"""Returns a short status"""
		try:
			return self.repo.git.status("-s")
		except Exception as e:
			return f"[ERROR] generating status: {e}"
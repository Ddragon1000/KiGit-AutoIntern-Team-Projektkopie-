from git import Repo

class GitManager:
	def __init__(self, path):
		self.repo = Repo(path)
	
	def get_change_status(self):
		return self.repo.is_dirty()
	
	def diff(self, commit: str = "HEAD", file: str = None):
		return self.repo.git.diff(f"{commit}", "--", f"{file}")

	def status(self):
		return self.repo.git.status("-s")

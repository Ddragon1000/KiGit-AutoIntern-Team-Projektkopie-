class DiffBody:

	added_objects = []
	removed_objects = []
	modified_objects = []

	def __init__(self):
		pass

	def get_num_added(self):
		return len(self.added_objects)

	def get_num_removed(self):
		return len(self.removed_objects)

	def get_num_modified(self):
		return len(self.modified_objects)

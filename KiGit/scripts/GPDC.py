class GPDC:
	"""General-Purpose-DataClass
	used to store some data for a specific type
	"""

	name = ""
	type = None
	attributes = []
	was_modified = False
	modified = []

	def __init__(self):
		pass

	def get_name(self):
		return self.name

	def get_type(self):
		return self.type

	def get_modified(self):
		return self.modified

	def get_attributes(self):
		return self.attributes

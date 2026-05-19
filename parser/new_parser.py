from dataclasses import dataclass
import unidiff

@dataclass
class DiffRes:
	added: int = 0
	removed: int = 0
	changed: int = 0

	def __str__(self):
		return(
			f"Added: 	{self.added}\n"
			f"Removed: 	{self.removed}\n"
			f"Modified: {self.changed}\n"
		)

#Registry for what file the parser is used
#easily add new filetypes if necessary later
FILE_PARSERS: dict[str, str] = {
	".kicad_sch": "wire",
	".kicad_pcb": "segment",
	#later e.g.:
	#".kicad_pcb": "via"
}

def get_keyword(path: str) -> str | None:
	"""return the S-Expression keyword for filepath"""
	for extension, keyword in FILE_PARSERS.items():
		if path.endswith(extension):
			return keyword
	return None

#counting logic
#if we are in a wire block -> if only added parts -> added
#						   -> if added and removed -> modified
#						   -> if only removed -> removed
def count_elements(patched_file: unidiff.PatchedFile, keyword: str) -> DiffRes:
	"""Counting added, removed and modified elements of one specific keyword of a patched file"""
	result = DiffRes()

	for hunk in patched_file:
		in_block = False
		depth = 0
		has_added = False
		has_removed = False

		for line in hunk:
			stripped = line.value.strip()

			if f"({keyword}" in stripped and not in_block:
				if line.is_added:
					result.added += 1
				elif line.is_removed:
					result.removed += 1
				else:
					in_block = True
					depth = 1
					has_added = False
					has_removed = False
			elif in_block:
				depth += stripped.count("(")
				depth -= stripped.count(")")

				if line.is_added:
					has_added = True
				elif line.is_removed:
					has_removed = True
				
				if depth <= 0:
					if has_added and has_removed:
						result.changed += 1
					in_block = False

	return result

#main parser
def parse(diff_path: str) -> dict[str, DiffRes]:
	"""Reading unified diff file and returns DiffRes for each filetype"""
	patch = unidiff.PatchSet.from_filename(diff_path, encoding="utf-8")
	results = {}

	for patched_file in patch:
		keyword = get_keyword(patched_file.path)
		if keyword is None:
			continue #unknown file -> ignore

		label = patched_file.path
		results[label] = count_elements(patched_file, keyword)

	return results
from dataclasses import dataclass
import io
import unidiff
from scripts.DiffRes import DiffRes
from scripts.BasicChange import *

@dataclass
class ParseRes:
	filename: str
	filetype: str
	result: DiffRes

class KiCadDiffParser:

	#Registry for what file the parser is used
	#easily add new filetypes if necessary later
	FILE_PARSERS: dict[str, str] = {
		".kicad_sch": "wire",
		".kicad_pcb": "segment",
		#later e.g.:
		#".kicad_pcb": "via"
	}

	def __init__(self):
		self.diffres = DiffRes(changes=[])

	#main parser
	def parse(self, diff_str: str) -> DiffRes:
		"""Reading unified diff file and returns DiffRes for each filetype"""
		diff_stream = io.StringIO(diff_str)
		patch = unidiff.PatchSet(diff_stream)


		for patched_file in patch:
			keyword = self._get_parser(patched_file.path)
			if keyword is None:
				continue #unknown file -> ignore

			self._count_elements(patched_file, keyword)

		return self.diffres

	def _get_parser(self, path: str) -> str | None:
		"""return the S-Expression keyword for filepath"""
		for extension, keyword in self.FILE_PARSERS.items():
			if path.endswith(extension):
				return keyword
		return None

	#counting logic
	#if we are in a wire block -> if only added parts -> added
	#						   -> if added and removed -> modified
	#						   -> if only removed -> removed
	def _count_elements(self, patched_file: unidiff.PatchedFile, keyword: str):
		"""Counting added, removed and modified elements of one specific keyword of a patched file"""

		for hunk in patched_file:
			in_block = False
			depth = 0
			has_added = False
			has_removed = False

			for line in hunk:
				stripped = line.value.strip()

				if f"({keyword}" in stripped and not in_block:
					if line.is_added:
						self.diffres.addChange(ComponentAdded(keyword, patched_file.path))
					elif line.is_removed:
						self.diffres.addChange(ComponentRemoved(keyword, patched_file.path))
					else:
						in_block = True
						depth = 2
						has_added = False
						has_removed = False
				elif in_block:
					depth += stripped.count("(")
					depth -= stripped.count(")")

					if line.is_added:
						has_added = True
					elif line.is_removed:
						has_removed = True
				
					if depth <= 1:
						if has_added and has_removed:
							self.diffres.addChange(ComponentModified(keyword, patched_file.path))
						in_block = False

		return True
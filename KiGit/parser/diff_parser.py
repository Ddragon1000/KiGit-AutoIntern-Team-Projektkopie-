from dataclasses import dataclass
import io
import unidiff
import kigit_globals

# File `AutoIntern-3\KiGit\parser\diff_parser.py` is part of an implicit namespace package. Add an `__init__.py`
# Missing docstring in public module
# Missing docstring in public class

@dataclass
class DiffRes:
	added: int = 0
	removed: int = 0
	modified: int = 0

	def __str__(self) -> str:
		return(
			f"Added: 	{self.added}\n"
			f"Removed: 	{self.removed}\n"
			f"Modified: {self.modified}\n"
		)

@dataclass
class ParseRes:
	filename: str
	filetype: str
	result: DiffRes

class KiCadDiffParser:

	#Registry for what file the parser is used
	#easily add new filetypes if necessary later

	def __init__(self):
		self.parse_results: list[ParseRes] = []

	#main parser
	def parse(self, diff_str: str) -> list[ParseRes]:
		"""Reading unified diff file and returns DiffRes for each filetype"""
		diff_stream = io.StringIO(diff_str)
		patch = unidiff.PatchSet(diff_stream)

		for patched_file in patch:
			keyword = self._get_parser(patched_file.path)
			if keyword is None:
				continue #unknown file -> ignore

			result = self._count_elements(patched_file, keyword)

			self.parse_results.append(ParseRes(
				filename = patched_file.path,
				filetype = keyword,
				result = result,
			))

		return self.parse_results

	#self is not used: [PLR6301]: Method `_get_parser` could be a function, class method, or static method
	def _get_parser(self, path: str) -> str | None:
		"""Return the S-Expression keyword for filepath"""
		for extension, keyword in kigit_globals.FILE_PARSERS.items():
			if path.endswith(extension):
				return keyword
		return None

	#counting logic
	#if we are in a wire block -> if only added parts -> added
	#						   -> if added and removed -> modified
	#						   -> if only removed -> removed

	#self is not used: [PLR6301]: Method `_count_elements` could be a function, class method, or static method
	#`_count_elements` is too complex (11 > 10)
	#Consider adding `@typing.override` if this method overrides a method from a superclass
	def _count_elements(self, patched_file: unidiff.PatchedFile, keyword: str) -> DiffRes:
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
							result.modified += 1
						in_block = False

		return result

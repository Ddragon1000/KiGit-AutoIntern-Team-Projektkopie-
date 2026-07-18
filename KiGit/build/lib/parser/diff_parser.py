import sexpdata
from dataclasses import dataclass
from scripts.DiffRes import DiffRes
import scripts.BasicChange as BasicChange
from git.diff import DiffIndex
from pathlib import Path
from kigit_globals import FILE_PARSERS
from scripts.helper import extract_parameters

class KiCadDiffParser:

	#Registry for what file the parser is used
	#easily add new filetypes if necessary later

	def __init__(self):
		self.diffres = DiffRes(changes=[])

	#main parser
	def parse(self, diff_index: DiffIndex, working_tree_dir: str = None) -> DiffRes:
		"""Reading unified diff file and returns DiffRes for each filetype"""

		for diff in diff_index:
			path = diff.b_path or diff.a_path
			keywords = self._get_keywords(path)
			if not keywords:
				continue #unknown file -> ignore
			#get blobs from gitpython
			old_text = diff.a_blob.data_stream.read().decode("utf-8") if diff.a_blob else ""
			if diff.b_blob:
				new_text = diff.b_blob.data_stream.read().decode("utf-8")
			elif diff.deleted_file:
				new_text = ""
			elif working_tree_dir and diff.b_path:
				new_text = Path(working_tree_dir, diff.b_path).read_text(encoding="utf-8")
			else:
				new_text = ""
			
			old_sexp = sexpdata.loads(old_text) if old_text else []
			new_sexp = sexpdata.loads(new_text) if new_text else []

			#parse python lists for each keyword
			for keyword in keywords:
				key_symbol = sexpdata.Symbol(keyword)

				#filter relevant elements
				key_symbol = sexpdata.Symbol(keyword)
				old_elements = [item for item in old_sexp if isinstance(item, list) and item[0] == key_symbol]
				new_elements = [item for item in new_sexp if isinstance(item, list) and item[0] == key_symbol]

				#compare symnatic for added, removed, modified
				self._compare_elements(old_elements, new_elements, keyword, path)

		return self.diffres

	def _get_keywords(self, path: str) -> list[str]| None:
		"""return the S-Expression keyword for filepath"""
		for extension, keywords in FILE_PARSERS.items():
			if path.endswith(extension):
				return keywords
		return None
	
	def _extract_coordinates(self, elements_list) -> list[tuple[float, float]]:
		"""
		Helperfunction: Extracts all (xy X Y) coords from elements
		"""
		coords = []

		def search_xy(item):
			if isinstance(item, list):
				if len(item) >= 3 and item[0] == sexpdata.Symbol('xy'):
					try:
						coords.append((float(item[1]), float(item[2])))
					except (ValueError, TypeError):
						pass
				else:
					for sub_item in item:
						search_xy(sub_item)
		
		search_xy(elements_list)
		return coords

	#counting logic
	#if we are in a wire block -> if only added parts -> added
	#						   -> if added and removed -> modified
	#						   -> if only removed -> removed
	def _compare_elements(self, old_elems, new_elems, keyword, path):
		"""Counting added, removed and modified elements of one specific keyword of a patched file"""

		#preselection whats identical is not important
		unmatched_old = [e for e in old_elems if e not in new_elems]
		unmatched_new = [e for e in new_elems if e not in old_elems]

		matched_old = []
		matched_new = []

		#get modified
		for old_el in unmatched_old:
			old_pts = self._extract_coordinates(old_el)
			if len(old_pts) < 2:
				continue

			for new_el in unmatched_new:
				if new_el in matched_new:
					continue
				
				new_pts = self._extract_coordinates(new_el)
				if len(new_pts) < 2:
					continue
				
				#if starting point equal but not end -> moidified
				if old_pts[0] != new_pts[0] or old_pts[1] != new_pts[1]:
					ref_string = sexpdata.dumps(new_el)

					self.diffres.addChange(BasicChange.ComponentMoved(
						reference=keyword,
						origin=path,
						component=ref_string,
						coordinates=(old_pts, new_pts)
					))
					matched_old.append(old_el)
					matched_new.append(new_el)
					break

		#everything else should be deleted or added
		for old_el in unmatched_old:
			if old_el not in matched_old:
				ref_string = sexpdata.dumps(old_el)
				self.diffres.addChange(BasicChange.ComponentRemoved(reference=keyword, origin=path, component=ref_string))

		for new_el in unmatched_new:
			if new_el not in matched_new:
				ref_string = sexpdata.dumps(new_el)
				self.diffres.addChange(BasicChange.ComponentAdded(reference=keyword, origin=path, component=ref_string))	

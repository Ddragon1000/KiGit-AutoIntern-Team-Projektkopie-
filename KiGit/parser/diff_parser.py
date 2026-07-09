import sexpdata
from dataclasses import dataclass
from scripts.DiffRes import DiffRes
import scripts.BasicChange as BasicChange
from git.diff import DiffIndex
from pathlib import Path
from kigit_globals import FILE_PARSERS

class KiCadDiffParser:

	def __init__(self):
		self.diffres = DiffRes(changes=[])

	def parse(self, diff_index: DiffIndex, working_tree_dir: str = None) -> DiffRes:
		"""Reading DiffIndex Object of GitPython and returns DiffRes for each filetype"""

		for diff in diff_index:
			self._process_diff(diff, working_tree_dir)
		return self.diffres
	
	def _process_diff(self, diff, working_tree_dir: str):
		path = diff.b_path or diff.a_path
		keyword = self._get_keyword(path)
		if not keyword:
			return
		old_elements = self._parse_elements(diff.a_blob, None, keyword)
		new_elements = self._parse_elements(diff.b_blob, working_tree_dir and Path(working_tree_dir, diff.b_path), keyword)
		self._compare_elements(old_elements, new_elements, keyword, path)
		
	def _parse_elements(self, blob, fallback_path, keyword) -> list:
		text = self._read_text(blob, fallback_path)
		if not text:
			return []
		sexp = sexpdata.loads(text)
		key_symbol = sexpdata.Symbol(keyword)
		return [item for item in sexp if isinstance(item, list) and item and item[0] == key_symbol]

	
	def _read_text(self, blob, fallback_path) -> str:
		if blob:
			return blob.data_stream.read().decode("utf-8")
		if fallback_path and fallback_path.exists():
			return fallback_path.read_text(encoding="utf-8")
		return ""
		

	def _compare_elements(self, old_elems, new_elems, keyword, path):
		"""Counting added, removed and modified elements of one specific keyword of a patched file"""

		#preselection whats identical is not important
		#only old elements in here if there are not a part of new elements
		unmatched_old = [elem for elem in old_elems if elem not in new_elems]
		#only new elements in here if there are not a part of old elements
		unmatched_new = [elem for elem in new_elems if elem not in old_elems]

		self._report_moved(unmatched_old, unmatched_new, keyword, path)

		#everything else should be deleted or added
		for old_el in unmatched_old:
			self.diffres.addChange(BasicChange.ComponentRemoved(reference=keyword, origin=path, component=sexpdata.dumps(old_el)))

		for new_el in unmatched_new:
				self.diffres.addChange(BasicChange.ComponentAdded(reference=keyword, origin=path, component=sexpdata.dumps(new_el)))

	def _report_moved(self, unmatched_old: list, unmatched_new: list, keyword: str, path: str):
		"""finds elements with same start or same endpoints and reports them as ComponentMoved or removes them out of both lists"""

		for old_el in list(unmatched_old):
			old_pts = self._extract_coordinates(old_el)
			if len(old_pts) < 2:
				continue

			match = self._find_moved_match(old_pts, unmatched_new)
			if match is None:
				continue

			new_el, new_pts = match
			self.diffres.addChange(BasicChange.ComponentMoved(
				reference=keyword, origin=path,
				component=new_el,
				coordinates=(old_pts, new_pts)
			))
			unmatched_old.remove(old_el)
			unmatched_new.remove(new_el)

	def _find_moved_match(self, old_pts, candidates: list):
		"""searches in candidates one element which start or endpoints are the same to old_pts but not both!"""

		for new_el in candidates:
			new_pts = self._extract_coordinates(new_el)
			if len(new_pts) < 2:
				continue

			start_same = old_pts[0] == new_pts[0]
			end_same = old_pts[1] == new_pts[1]
			if start_same != end_same:
				return new_el, new_pts
		return None

	def _get_keyword(self, path: str) -> str | None:
		"""return the S-Expression keyword for filepath"""
		for extension, keyword in FILE_PARSERS.items():
			if path.endswith(extension):
				return keyword
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

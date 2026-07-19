import sexpdata
from typing import Any, Optional
from dataclasses import dataclass
from scripts.DiffRes import DiffRes
import scripts.BasicChange as BasicChange
from git import Blob, IndexObject
from git.diff import Diff, DiffIndex
from pathlib import Path
from kigit_globals import FILE_PARSERS
from scripts.helper import extract_parameters
from kigit_globals import COORDINATE_LEN
from kigit_globals import SEXP_BLOCK_CONTENTS

class KiCadDiffParser:

	def __init__(self):
		self.diffres = DiffRes(changes=[])

	def parse(self, diff_index: DiffIndex, working_tree_dir: Optional[str] = None) -> DiffRes:
		"""Reading DiffIndex Object of GitPython and returns DiffRes for each filetype"""

		for diff in diff_index:
			self._process_diff(diff, working_tree_dir)
		return self.diffres
	
	def _process_diff(self, diff: Diff, working_tree_dir: Optional[str]) -> None:
		path = diff.b_path or diff.a_path
		if path is None:
			return
		keywords = self._get_keywords(path)
		if not keywords:
			return
		for keyword in keywords:
			old_elements = self._parse_elements(diff.a_blob, None, keyword)
			new_elements = self._parse_elements(
				diff.b_blob,
				Path(working_tree_dir, diff.b_path) if working_tree_dir and diff.b_path else None,
				keyword)
			self._compare_elements(old_elements, new_elements, keyword, path)
		
	def _parse_elements(self, blob: Optional[IndexObject], 
					 fallback_path: Optional[Path], keyword: str) -> list[list[Any]]:
		text = self._read_text(blob, fallback_path)
		if not text:
			return []
		sexp = sexpdata.loads(text)
		key_symbol = sexpdata.Symbol(keyword)
		return [item for item in sexp if isinstance(item, list) and item and item[0] == key_symbol]

	
	def _read_text(self, blob: Optional[IndexObject], fallback_path: Optional[Path]) -> str:
		if blob:
			return blob.data_stream.read().decode("utf-8")
		if fallback_path and fallback_path.exists():
			return fallback_path.read_text(encoding="utf-8")
		return ""
		

	def _compare_elements(self, old_elems: list[list[Any]], 
					   new_elems: list[list[Any]], keyword: str, path: str):
		"""Counting added, removed and modified elements of one specific keyword of a patched file"""

		#preselection whats identical is not important
		#only old elements in here if there are not a part of new elements
		unmatched_old = [elem for elem in old_elems if elem not in new_elems]
		#only new elements in here if there are not a part of old elements
		unmatched_new = [elem for elem in new_elems if elem not in old_elems]

		self._report_moved(unmatched_old, unmatched_new, keyword, path)

		#everything else should be deleted or added
		for old_el in unmatched_old:
			self.diffres.addChange(BasicChange.ComponentRemoved(
				reference=keyword, 
				origin=path, 
				component=sexpdata.dumps(old_el)))

		for new_el in unmatched_new:
				self.diffres.addChange(BasicChange.ComponentAdded(
					reference=keyword, 
					origin=path, 
					component=sexpdata.dumps(new_el)))

	def _report_moved(self, unmatched_old: list[list[Any]], 
				   unmatched_new: list[list[Any]], keyword: str, path: str) -> None:
		"""finds elements with same start or same endpoints 
		and reports them as ComponentMoved or removes them out of both lists"""

		for old_el in list(unmatched_old):
			old_pts = self._extract_coordinates(old_el)
			if len(old_pts) < COORDINATE_LEN:
				continue

			match = self._find_moved_match(old_pts, unmatched_new)
			if match is None:
				continue

			new_el, new_pts = match
			self.diffres.addChange(BasicChange.ComponentMoved(
				reference=keyword, origin=path,
				component=sexpdata.dumps(new_el),
				coordinates=(old_pts, new_pts)
			))
			unmatched_old.remove(old_el)
			unmatched_new.remove(new_el)

	def _find_moved_match(self, old_pts: list[tuple[float, float]], 
					   candidates: list[list[Any]]) -> Optional[tuple[list[Any], list[tuple[float, float]]]]:
		"""searches in candidates one element which start or endpoints are the same to old_pts but not both!"""

		for new_el in candidates:
			new_pts = self._extract_coordinates(new_el)
			if len(new_pts) < COORDINATE_LEN:
				continue

			start_same = old_pts[0] == new_pts[0]
			end_same = old_pts[1] == new_pts[1]
			if start_same != end_same:
				return new_el, new_pts
		return None

	def _get_keywords(self, path: str) -> Optional[list[str]]:
		"""return the S-Expression keyword for filepath"""
		for extension, keywords in FILE_PARSERS.items():
			if path.endswith(extension):
				return keywords
		return None
	
	def _extract_coordinates(self, elements_list: list[Any]) -> list[tuple[float, float]]:
		"""
		Helperfunction: Extracts all (xy X Y) coords from elements
		"""
		coords = []

		def search_xy(item):
			if isinstance(item, list):
				if len(item) >= SEXP_BLOCK_CONTENTS and item[0] == sexpdata.Symbol('xy'):
					try:
						coords.append((float(item[1]), float(item[2])))
					except (ValueError, TypeError):
						pass
				else:
					for sub_item in item:
						search_xy(sub_item)
		
		search_xy(elements_list)
		return coords

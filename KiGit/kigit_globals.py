"""Global variables"""

FILE_PARSERS: dict[str, list[str]] = {
	".kicad_sch": ["wire", 
				"bus", 
				"symbol", 
				"lib_symbols", 
				"junction", 
				"no_connect", 
				"label", 
				"global_label", 
				"hierachical_label", 
				"sheet", 
				"polyline", 
				"text", 
				"rectangle", 
				"circle"],
	".kicad_pcb": ["footprint", 
				"pad", 
				"arc", 
				"via", 
				"segment", 
				"zone", 
				"gr_line", 
				"gr_arc", 
				"gr_circle", 
				"gr_poly", 
				"gr_text", 
				"dimension"],
	#later e.g.:
	#".kicad_pcb": "via"s
}


COORDINATE_LEN = 2
SEXP_BLOCK_CONTENTS = 3

# here small things to keep track of mkdocs variables
from dataclasses import dataclass

@dataclass
class CMD:
	diff: str
	status: str

@dataclass
class GIT_INTERFACE:
	gitDiff: str
	gitStatus: str

@dataclass
class GETTING_STARTED:
	overview: str

@dataclass
class MISCELLANEOUS:
	license: str
	releases: str

@dataclass
class DOCS:
	index: str
	cmd: CMD
	git_interface: GIT_INTERFACE
	misc: MISCELLANEOUS

# here define project folder paths to files
docs = DOCS(index= "",
			cmd=CMD("", ""), 
			git_interface=GIT_INTERFACE("", ""),
			misc=MISCELLANEOUS("", "")
			)
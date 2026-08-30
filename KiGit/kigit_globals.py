"""
MIT License

Copyright (c) Jannick Tim Medda, Dennis Piotrowski, Marcel Wiemann, Ismail Koc, Daniel Quayes, Adrian Sturm

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
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
from pathlib import Path
from importlib import resources

ROOT = Path(__file__).resolve().parent

DOCS_DIR = Path(str(resources.files("kigit_site")))

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
docs = DOCS(index= str(DOCS_DIR / "index.html"),
			cmd=CMD(
				diff=str(DOCS_DIR / "commands" / "diff.html"),
		    	status=str(DOCS_DIR / "commands" / "status.html")
				), 
			git_interface=GIT_INTERFACE(
				gitDiff=str(DOCS_DIR / "git_interface" / "git_diff.html"),
				gitStatus=str(DOCS_DIR / "git_interface" / "git_status.html")
			),
			misc=MISCELLANEOUS(
				license=str(DOCS_DIR / "Miscellaneous" / "license.html"),
				releases=str(DOCS_DIR / "Miscellaneous" / "releases.html")
			)
			)

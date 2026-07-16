"""Global variables"""

FILE_PARSERS: dict[str, str] = {
	".kicad_sch": "wire",
	".kicad_pcb": "segment",
	#later e.g.:
	#".kicad_pcb": "via"s
}

 
COORDINATE_LEN = 2
SEXP_BLOCK_CONTENTS = 3
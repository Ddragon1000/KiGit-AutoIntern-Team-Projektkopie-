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
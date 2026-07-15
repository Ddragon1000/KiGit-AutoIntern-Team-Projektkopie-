"""Global variables"""

FILE_PARSERS: dict[str, list[str]] = {
	".kicad_sch": ["wire", "symbol"],
	".kicad_pcb": ["segment"],
	#later e.g.:
	#".kicad_pcb": "via"
}

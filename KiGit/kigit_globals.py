"""Global variables"""

FILE_PARSERS: dict[str, str] = {
	".kicad_sch": "wire",
	".kicad_pcb": "segment",
	#later e.g.:
	#".kicad_pcb": "via"
}

FILE_ENDINGS: dict[str, str] = {
    "sch": "kicad_sch",
    "pcb": "kicad_pcb"

}
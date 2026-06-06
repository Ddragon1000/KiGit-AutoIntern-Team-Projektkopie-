from typer.testing import CliRunner
from main import app

runner = CliRunner()

def test_missing_diff_file():
    result = runner.invoke(app, [""])
    assert result.exit_code != 0

def test_diff_executes():
    result = runner.invoke(app, ["diff"])
    assert result.exit_code == 0

def test_wires_line_values():
    result = runner.invoke(app, ["diff"])
    output_lines = result.stdout.splitlines()    #splits each row form the table into lines

    wires_line = None

    for line in output_lines:   # searches for the wires row/line
        if "wires" in line:
            wires_line = line      # extracts it if found

    assert wires_line is not None

    wires_line = wires_line.split("│")  # splits the values of the columns for better comparison later
    wires_box = []
    for col in wires_line:
        if col != "":
            wires_box.append(col.strip())   #only takes important values and adds them without empty spaces

    assert wires_box[0] == "wires"     #checks if value of table is equal to expected value
    assert wires_box[1] == "2"         #removed
    assert wires_box[2] == "2"         #added
    assert wires_box[3] == "0"         #modified

def test_segments_line_values(): #Same execution as above
    result = runner.invoke(app, ["diff"])
    output_lines = result.stdout.splitlines()

    segments_line = None

    for line in output_lines:
        if "segments" in line:
            segments_line = line

    assert segments_line is not None

    segments_line = segments_line.split("│")
    segments_box = []

    for col in segments_line:
        if col != "":
            segments_box.append(col.strip())

    assert segments_box[0] == "segments"
    assert segments_box[1] == "0"
    assert segments_box[2] == "0"
    assert segments_box[3] == "0"

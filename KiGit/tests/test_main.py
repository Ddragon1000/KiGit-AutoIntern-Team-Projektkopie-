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
from typer.testing import CliRunner
from main import app

#File `tests\test_main.py` is part of an implicit namespace package. Add an `__init__.py`

runner = CliRunner()

def test_missing_diff_file() -> None:
    result = runner.invoke(app, [""])
    assert result.exit_code != 0

def test_diff_executes() -> None:
    result = runner.invoke(app, ["diff"])
    assert result.exit_code == 0

def test_wires_line_values() -> None:
    result = runner.invoke(app, ["diff"])
    output_lines = result.stdout.splitlines()    #splits each row form the table into lines

    wires_line = None

    #Replace for loop with list comprehension
    for line in output_lines:   # searches for the wires row/line
        if "wires" in line:
            wires_line = line      # extracts it if found

    assert wires_line is not None

    wires_line = wires_line.split("│")  # splits the values of the columns for better comparison later
    wires_box = []

    #Replace for loop with list comprehension
    for col in wires_line:
        # `col != ""` can be simplified to `col` as an empty string is falsy
        if col:
            wires_box.append(col.strip())   #only takes important values and adds them without empty spaces

    assert wires_box[0] == "wires"     #checks if value of table is equal to expected value
    assert wires_box[1] == "2"         #removed
    assert wires_box[2] == "2"         #added
    assert wires_box[3] == "0"         #modified

def test_segments_line_values() -> None: #Same execution as above
    result = runner.invoke(app, ["diff"])
    output_lines = result.stdout.splitlines()

    segments_line = None

    for line in output_lines:
        if "segments" in line:
            segments_line = line

    assert segments_line is not None

    segments_line = segments_line.split("│")
    segments_box = []

    #Replace for loop with list comprehension to create a transformed list
    for col in segments_line:
        # `col != ""` can be simplified to `col` as an empty string is falsy
        if col:
            segments_box.append(col.strip())

    assert segments_box[0] == "segments"
    assert segments_box[1] == "0"
    assert segments_box[2] == "0"
    assert segments_box[3] == "0"

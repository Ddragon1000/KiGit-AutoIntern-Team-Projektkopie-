<!-->
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
<-->
# Welcome to Kigit

Kigit aids hardware developers to identify relevant KiCad project changes.

Changes made in KiCad projects can be easily seen visually while working in KiCad. However, these visual changes do not translate well in written form. Hence it can be difficult for hardware developers to assess their changes by reading KiCad files natively. This problem is exemplified by comparing two files using the `diff` command. Hardware developers that use `git` for versioning their changes have to laboriously look through the generated output to then decide what changes are now relevant to for the progress of their project. Furthermore, mistakes may result in additional development cycles due to the resulting faulty hardware.

To remedy this issue Kigit serves as an automated comparison tool that will show the developer what and how many changes were made between two versions of a file. It does so by:

* Counting made changes to specified KiCad components (such as wires)

## Why Kigit?
Kigit's main distinction between existing tools is...

More differences can be found [here](./getting_started/overview.md). 

## How to install

#### With a Wheel File
* `uv tool install <path to .whl>`
####In Project Folder KiGit
* `uv tool install .`

## Brief overview of commands

* [`kigit diff`](../Kigit_Commands/kigit Diff.md) - .
* [`kigit status`](../Kigit_Commands/kigit Status.md) - .

## Supported file types and components
* [`kicad_sch`](../Supported_File_Types/kicad_sch.md)
* [`kicad_pcb`](../Supported_File_Types/kicad_pcb.md)

## Project layout

    mkdocs.yml    # The configuration file of MkDocs.
    docs/         # MkDocs Documentation pages
        index.md  # The documentation homepage.
        ...       # Other markdown pages, images and other files.
    parser/
        parser.py
    scripts/
        Git_Commands.py
    tests/
        Git_Commands_tests.py
        test_main.py
    main.py
# Welcome to Kigit

Kigit aids hardware developers to identify relevant KiCad project changes.

Changes made in KiCad projects can be easily seen visually while working in KiCad. However, these visual changes do not translate well in written form. Hence it can be difficult for hardware developers to assess their changes by reading KiCad files natively. This problem is exemplified by comparing two files using the `diff` command. Hardware developers that use `git` for versioning their changes have to laboriously look through the generated output to then decide what changes are now relevant to for the progress of their project. Furthermore, mistakes may result in additional development cycles due to the resulting faulty hardware.

To remedy this issue Kigit serves as an automated comparison tool that will show the developer what and how many changes were made between two versions of a file. It does so by:

* Counting made changes to specified KiCad components (such as wires)

## Why Kigit?
Kigit's main distinction between existing tools is...

More differences can be found [here](./why_kigit.md). 

## How to install
<<<<<<< HEAD
#### With a Wheel File
* `uv tool install <path to .whl>`
####In Project Folder KiGit
* `uv tool install .`

## Brief overview of commands

* [`kigit diff`](../Kigit_Commands/kigit Diff.md) - .
* [`kigit status`](../Kigit_Commands/kigit Status.md) - .
=======
* `pip install kigit`

## Brief overview of commands

* [`kigit gitDiff`](../Kigit_Commands/gitDiff.md) - .
* [`kigit gitStatus`](../Kigit_Commands/gitStatus.md) - .
>>>>>>> main

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
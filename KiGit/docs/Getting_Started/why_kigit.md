# Why Kigit?

Kigit is by far not the first project that attempts to aid hardware developers to identify relevant changes in their KiCad projects.

The main difference between Kigit and other tools is...

## Other tools for kicad diffs

Here are some other noteworthy tools listed and how Kigit differs from them:
<br />
<br />

### Plotkicadsch
This project contains "Plotgitsch", a command line tool which generates visual Diffs for KiCad-Schematics. It uses Git to compare to different versions and opens the differences as color coded SVGs in a browser tab.

#### How Kigit differs from Plotkicadsch
Kigit is practically fully committed to depicting changes (diffs) of KiCad files, where as the main functionality of Plotkicadsch is to export Kicad Schematic files to SVG pictures. But it also contains plotgitsch to visualize git diffs between two Kicad Schematic files.<br />
The biggest difference is the visualization of the diffs. Whereas Plotkicadsch exports the diff to an SVG picture, that is then opened with a browser, Kigit's main output is a table in the console of the command line interface that is being used. 
<br />
<br />

### Kicad-gitdiff-cli
A python based tool developed to be especially compatible for KiCad 8 and higher. It generates simple visual diffs for boards by using kicad-cli to compare Layer-exports.

#### How Kigit differs from Kicad-gitdiff-cli
Kicad-gitdiff-cli is a tool to create pictures of KiCad schematic diffs. When installed, a git repository can be initialized with the tool, modifying the git diff command to instead output an image that shows the diffs. Unlike Kigit, it has minimal dependencies and is transparently integrated into git, meaning you can just use the git command like always, while Kicad-gitdiff-cli generates an image in the background. Kigit on the other hand comes with it's own kigit commands. KiGit supports PCB files as well, while Kicad-gitdiff-cli doesn't yet. And the output of KiGit is very different, the main output being a table of the wires or segments that have been changed.
<br />
<br />

### KiCad-Diff
A known Open-Source-Script which is usually integrated into Web-interfaces to make Layout-changes visible via ”Blinking” (fast change between old and new)

#### How Kigit differs from KiCad-Diff
KiCad-Diff is mostly used with Web-interfaces, generating images of the new and old pcb layout on top of each other, allowing the user to see changes by fast alternating between old and new, also called "blinking". This is very different to KiGit's main use, which counts the amount of wires or segments of Kicad schematic files and Kicad PCB files, that have been modified, added or removed, and outputs the result to a table. KiGit also supports both schematic and PCB files, whereas KiCad-Diff is solely for PCB files. 
<br />
<br />

### Difftastic
A structural Diff-Tool which compares the Code with it's Syntax-Trees (S-Expressions) instead of parsing line by line. Since KiCad-Files are based on S-Expressions, Difftastic is the best tool for most cases to group the changes in a diff than the standard git diff. 

#### How Kigit differs from Difftastic
Difftastic's main difference is that it can be applied to many different files, not only KiCad files. Kigit on the other hand is very much directed towards Kicad only. 
<br />
<br />

### Semantic Diff
A commercial/Freemium Tool specialized on detecting shifted code and other changes (such as comments or formats, which are in turn ignored). It can be easily integrated into VS Code.

#### How Kigit differs from Semantic Diff
Semantic Diff is a tool that can be integrated into VS Code, which then allows the user to understand git diffs of their code easier. It also supports up to 14 different programming languages. It's entire application area is quite different to Kigit, which only focuses on Kicad files. 
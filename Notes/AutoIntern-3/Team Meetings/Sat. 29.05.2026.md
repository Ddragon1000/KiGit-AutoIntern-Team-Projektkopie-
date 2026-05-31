## Agenda:
- Progress on Documentation
- Progress on the new Git Library
- Summary of AutoIntern Meeting by Dennis
- Our Motivation on pushing forward

## Protocol:

### Progress on Documentation:
Dennis worked on a working half automatic documentation site working on a localhost server.
It is important for everyone working on code to properly comment out is functions, classes in fact everything, correctly, so that the automatic part of the documentation part is documented automatically.

### Progress on the new Git Library:
Jannick looked at the GitPython library. It will very simplify the way we worked before. With a small class holding methods which do the work of communicating with Git. For further interest look at [[Overview]] at the linked documentation page.

### Summary of AutoIntern Meeting by Dennis:
Overall was the Meeting with the AutoIntern Crew very exiting and interesting, as Dennis said. It brought many ideas and perspectives on how to further work on our project. 
These are the most important points:
- Output of KiGit should be on **one page** of a console, so no scrolling is needed
- Information should be reduced to the most important, e.g. if there are changes in files, the first command should only say, *hey there were changed*, with another command showing what exactly changed
- KiGit should detect custom objects (footprints, schematics ...)
- Detect faulty files and where the faulty part is
- files that are not KiCad files should not be recognized by KiGit and therefore not be reviewed by us
- **Optional**: check if connections are connected to each other 
- First check logical model of files and then compare them (ask Tabea)
- **NO** git add/git commit interface should be implemented
- It should be shown if electrical connection partners, positions, identifier, reference specifier, PCB wires, edgecut or the 3D model was changed
- Main purpose should propose a good description for a diff and merge on what changes were made
- if changes are in a diff, when committing confirmation for merge is  needed

### Our Motivation on pushing forward:
It is important to have similar goals when working as a team on such a project. This project should be used for everyone's benefit on getting experience working in a team, for a company objective, and especially getting experience in developing a software that is somewhat working as intended at the end. Everyone of us should work towards this goal.
# KiGit Tool
*AutoIntern-3*
> A CLI tool that helps the user track changes in KiCad projects with Git.

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)

--- 

## Motivation
*Why KiGit?*
Standard GIt diffs for KiCad schematics (`.kicad_sch`) and PCB (`.kicad_pcb`) files consists of S-expressions that are virtually unreadable in plain text.

**KiGit** solves this by parsing these file formats and condensing the raw `git diff` output into clear, structured, and color-coded terminal tables. This enables hardware developers to instantly spot modified, added, or deleted components and assess changes at a glance.

---

## Installation Guide
Follow these steps to install KiGit on your system:

### Prerequisites
* Python 3.10+
* [uv](https://github.com/astral-sh/uv) 

### Standard Installation (via git clone)
1. Clone the repository:
   ```bash
   git clone https://github.com/RUB-SELAB-2026/AutoIntern-3.git
   cd AutoIntern-3/KiGit
2. install KiGit via uv:
   ```bash
   uv tool install .

### Alternative Installation (via whl file)
1. Download the newest `.whl` file from Releases.
2. Open your terminal and install it via `uv`:
   ```bash
   `uv tool install <path-to-whl-file>`

## Updating
When updates of KiGit are available, pull the changes and reinstall:
1.  ```bash
    git pull
    uv tool install --reinstall .

---
## Quick Start

After installation, navigate to your KiCad project directory. Make sure your project is version-controlled with Git and has at least one commit.

1. Open a terminal in your KiCad project directory and run:
   ```bash
   kigit status
   kigit diff

### Markdown
* **`kigit status`**
  Displays an overview of modified, deleted or untracked files in your working directory
* **`kigit diff`**
  Generates a summary of changes (added, removed or modified components
* **`kigit diff -- details all`**
  provides a deeper analysis into specific symbol and layout modifications

---

## Documentation
Need more detailed guides or advanced configuration options for KiGit?  
Check out our documentation built with **MkDocs** to learn more about the different output formats, detailed diff modes etc.:
1. Open a terminal in the `KiGit` directory:
   ```bash
   kigit --docs

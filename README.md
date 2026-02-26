# Fix-PDF

A simple tool to remove restrictions and passwords from PDF files.

If you have a PDF that cannot be imported into apps like Samsung Notes due to "secure document" restrictions, or if you want to permanently remove a known password from a PDF, this script will do it.

## Requirements

- Python 3.x
- Required packages (install via pip):

```bash
pip install -r requirements.txt
```

*Note: On Windows, if you plan to use the command-line version, you also need `windows-curses` (`pip install windows-curses`).*

## Usage

The project includes two versions: a graphical interface (GUI) and a command-line interface (CLI).

### GUI Version (Tkinter)
Run the graphical version:
```bash
python fixpdf.py
```

### CLI Version (ncurses)
Run the terminal version:
```bash
python fixpdf_cmd.py
```

## Building an Executable

You can create a standalone executable using PyInstaller:

```bash
pyinstaller --onefile fixpdf.py
```
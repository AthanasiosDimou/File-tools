# PPT to PDF Converter

A cross-platform Python GUI application to convert PowerPoint presentations (`.ppt`, `.pptx`, `.ppsx`) to PDF using system-agnostic tools.

## Features

- 🖥️ **Cross-Platform**: Works on Windows, macOS, and Linux
- ⚡ **System Tools**: Uses native/pre-installed tools (no expensive licenses needed)
- 🎨 **GUI Interface**: Simple, clean interface built with PySide6
- 🔄 **Batch Processing**: Convert multiple files at once
- 📊 **Progress Tracking**: Real-time progress bar and status updates

## Installation

### Prerequisites

1. **Python 3.10+** (required for `match/case` statement support)

2. **PySide6** (GUI framework)
   ```bash
   pip install -r requirements.txt
   ```

### Platform-Specific Setup

#### Windows
- **PowerPoint**: Requires Microsoft Office (PowerPoint) to be installed
- **Dependencies**: 
  ```bash
  pip install comtypes
  ```
  (automatically installed via requirements.txt)

#### macOS
- **LibreOffice**: Install from [libreoffice.org](https://www.libreoffice.org/download/) or Homebrew:
  ```bash
  brew install libreoffice
  ```

#### Linux

**Ubuntu/Debian:**
```bash
sudo apt-get install libreoffice
```

**Fedora:**
```bash
sudo dnf install libreoffice
```

**Arch Linux:**
```bash
sudo pacman -S libreoffice-fresh
```

## Usage

Run the application:
```bash
python ppt_to_pdf.py
```

1. Click **"Select Files & Convert"**
2. Choose one or more PowerPoint files
3. Wait for the conversion to complete
4. PDFs will be saved in the same directory as the original files

## How It Works

The application uses `match/case` statements for clean, platform-agnostic logic:

- **Windows**: Leverages PowerPoint COM objects via `comtypes` for native conversion
- **macOS & Linux**: Uses LibreOffice's headless mode for reliable, free PDF export

## Technical Details

- Uses Python 3.10+ `match/case` instead of if/elif chains
- Runs conversion in background thread to keep GUI responsive
- Automatically detects available platform tools
- Provides platform-specific error messages with installation instructions

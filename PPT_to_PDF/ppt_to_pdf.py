import os
import sys
import subprocess
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel,
                               QPushButton, QProgressBar, QFileDialog, QMessageBox)
from PySide6.QtCore import QThread, Signal, Qt

# --- 1. Worker Thread for Background Processing ---
class ConversionWorker(QThread):
    progress_max = Signal(int)
    progress_update = Signal(int)
    status_update = Signal(str)
    error_occurred = Signal(str)
    finished_conversion = Signal(int)

    def __init__(self, file_paths):
        super().__init__()
        self.file_paths = file_paths

    def run(self):
        total_files = len(self.file_paths)
        self.progress_max.emit(total_files)

        # Determine platform and initialize required tools
        platform = self._get_platform()
        powerpoint = None

        match platform:
            case "windows":
                powerpoint = self._initialize_windows()
                if powerpoint is None:
                    return
            case "macos":
                if not self._check_libreoffice_macos():
                    return
            case "linux":
                if not self._check_libreoffice_linux():
                    return

        for i, file_path in enumerate(self.file_paths):
            file_path = os.path.abspath(file_path)
            output_path = os.path.splitext(file_path)[0] + ".pdf"
            filename = os.path.basename(file_path)

            self.status_update.emit(f"Converting: {filename}...")

            try:
                match platform:
                    case "windows":
                        self._convert_windows(powerpoint, file_path, output_path)
                    case "macos":
                        self._convert_libreoffice(file_path, output_path, "/Applications/LibreOffice.app/Contents/MacOS/soffice")
                    case "linux":
                        self._convert_libreoffice(file_path, output_path, "libreoffice")
            except Exception as e:
                self.status_update.emit(f"Failed to convert {filename}: {e}")

            self.progress_update.emit(i + 1)

        if platform == "windows" and powerpoint:
            powerpoint.Quit()

        self.finished_conversion.emit(total_files)

    def _get_platform(self):
        """Detect the current platform."""
        match sys.platform:
            case platform if platform.startswith("win"):
                return "windows"
            case "darwin":
                return "macos"
            case _:
                return "linux"

    def _initialize_windows(self):
        """Initialize PowerPoint COM object for Windows."""
        try:
            import comtypes.client
            powerpoint = comtypes.client.CreateObject("Powerpoint.Application")
            return powerpoint
        except ImportError:
            self.error_occurred.emit("The 'comtypes' package is missing.\nInstall with: pip install comtypes")
            return None
        except Exception as e:
            self.error_occurred.emit(f"Could not open PowerPoint. Is Microsoft Office installed?\nError: {e}")
            return None

    def _check_libreoffice_macos(self):
        """Check if LibreOffice is available on macOS."""
        lo_path = "/Applications/LibreOffice.app/Contents/MacOS/soffice"
        if not os.path.exists(lo_path):
            self.error_occurred.emit(
                "LibreOffice is not installed.\n"
                "Install from: https://www.libreoffice.org/download/\n"
                "or use Homebrew: brew install libreoffice"
            )
            return False
        return True

    def _check_libreoffice_linux(self):
        """Check if LibreOffice is available on Linux."""
        try:
            subprocess.run(["which", "libreoffice"], check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError:
            self.error_occurred.emit(
                "LibreOffice is not installed.\n"
                "Install on Ubuntu/Debian: sudo apt-get install libreoffice\n"
                "Install on Fedora: sudo dnf install libreoffice\n"
                "Install on Arch: sudo pacman -S libreoffice-fresh"
            )
            return False

    def _convert_windows(self, powerpoint, file_path, output_path):
        """Convert PPT to PDF on Windows using PowerPoint COM object."""
        ppFixedFormatTypePDF = 2
        ppFixedFormatIntentScreen = 1
        msoFalse = 0

        deck = powerpoint.Presentations.Open(file_path, WithWindow=False)
        deck.ExportAsFixedFormat(
            output_path,
            ppFixedFormatTypePDF,
            Intent=ppFixedFormatIntentScreen,
            PrintHiddenSlides=msoFalse,
            FrameSlides=msoFalse
        )
        deck.Close()

    def _convert_libreoffice(self, file_path, output_path, lo_cmd):
        """Convert PPT to PDF on macOS/Linux using LibreOffice."""
        output_dir = os.path.dirname(file_path)
        subprocess.run(
            [lo_cmd, '--headless', '--convert-to', 'pdf', file_path, '--outdir', output_dir],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )


# --- 2. Main GUI Application ---
class PptToPdfApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PPT to PDF Converter")
        self.setFixedSize(450, 200)

        # Layout
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # UI Elements
        self.label = QLabel("Select PowerPoint files to convert to PDF")
        self.label.setAlignment(Qt.AlignCenter)
        font = self.label.font()
        font.setPointSize(12)
        self.label.setFont(font)
        layout.addWidget(self.label)

        self.select_btn = QPushButton("Select Files & Convert")
        self.select_btn.setMinimumHeight(35)
        self.select_btn.clicked.connect(self.start_conversion)
        layout.addWidget(self.select_btn)

        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        layout.addWidget(self.progress)

        self.status_label = QLabel("Waiting for files...")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: gray;")
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def start_conversion(self):
        # Open file manager
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select PowerPoint Files",
            "",
            "PowerPoint Files (*.ppt *.pptx *.ppsx)"
        )

        if not file_paths:
            return

        self.select_btn.setEnabled(False)
        self.progress.setValue(0)
        self.status_label.setStyleSheet("color: black;")

        # Start background worker
        self.worker = ConversionWorker(file_paths)

        # Connect worker signals to UI updates
        self.worker.progress_max.connect(self.progress.setMaximum)
        self.worker.progress_update.connect(self.progress.setValue)
        self.worker.status_update.connect(self.status_label.setText)
        self.worker.error_occurred.connect(self.show_error)
        self.worker.finished_conversion.connect(self.finish_conversion)

        self.worker.start()

    def show_error(self, message):
        self.status_label.setText("Error occurred.")
        self.status_label.setStyleSheet("color: red;")
        QMessageBox.critical(self, "Error", message)
        self.select_btn.setEnabled(True)

    def finish_conversion(self, total):
        self.status_label.setText("Conversion Completed!")
        self.status_label.setStyleSheet("color: green;")
        QMessageBox.information(self, "Success", f"Successfully converted {total} file(s) to PDF!")
        self.select_btn.setEnabled(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Modernizing the UI look for cross-platform (optional)
    app.setStyle("Fusion")

    window = PptToPdfApp()
    window.show()
    sys.exit(app.exec())

import os
import sys
import subprocess
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel,
                               QPushButton, QProgressBar, QFileDialog, QMessageBox)
from PySide6.QtCore import QThread, Signal, Qt

# --- 1. Worker Thread for Background Processing ---
class ConversionWorker(QThread):
    # Define signals to communicate safely with the main GUI thread
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

        is_windows = sys.platform.startswith("win")
        powerpoint = None

        if is_windows:
            try:
                import comtypes.client
                self.pdf_format_code = 32 # VBA code for pptSaveAsPDF
                powerpoint = comtypes.client.CreateObject("Powerpoint.Application")
            except ImportError:
                self.error_occurred.emit("The 'comtypes' package is missing. Please install it.")
                return
            except Exception as e:
                self.error_occurred.emit(f"Could not open PowerPoint. Is Microsoft Office installed?\nError: {e}")
                return

        for i, file_path in enumerate(self.file_paths):
            file_path = os.path.abspath(file_path)
            output_path = os.path.splitext(file_path)[0] + ".pdf"
            filename = os.path.basename(file_path)

            self.status_update.emit(f"Converting: {filename}...")

            try:
                if is_windows:
                    # Windows Conversion
                    deck = powerpoint.Presentations.Open(file_path, WithWindow=False)
                    deck.SaveAs(output_path, self.pdf_format_code)
                    deck.Close()
                else:
                    # macOS/Linux Conversion
                    output_dir = os.path.dirname(file_path)

                    if sys.platform == "darwin": # macOS
                        lo_cmd = "/Applications/LibreOffice.app/Contents/MacOS/soffice"
                    else: # Linux
                        lo_cmd = "libreoffice"

                    subprocess.run([lo_cmd, '--headless', '--convert-to', 'pdf', file_path, '--outdir', output_dir],
                        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                    )
            except Exception as e:
                print(f"Failed to convert {filename}: {e}")

            # Send progress update to GUI
            self.progress_update.emit(i + 1)

        # Cleanup PowerPoint process on Windows
        if is_windows and powerpoint:
            powerpoint.Quit()

        self.finished_conversion.emit(total_files)


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

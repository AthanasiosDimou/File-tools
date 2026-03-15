in arch you will need to download libre office: `sudo pacman -S libreoffice-fresh`

or you can use this:

```py

import aspose.slides as slides

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

        for i, file_path in enumerate(self.file_paths):
            file_path = os.path.abspath(file_path)
            output_path = os.path.splitext(file_path)[0] + ".pdf"
            filename = os.path.basename(file_path)
            
            self.status_update.emit(f"Converting: {filename}...")

            try:
                # Use Aspose.Slides to render the PDF directly
                presentation = slides.Presentation(file_path)
                presentation.save(output_path, slides.export.SaveFormat.PDF)
            except Exception as e:
                print(f"Failed to convert {filename}: {e}")

            self.progress_update.emit(i + 1)

        self.finished_conversion.emit(total_files)
        
```

it does not use libre office but leaves a watermark and needs this package too expept from pyside6: aspose.slides>=24.1.0


if you want to delete it from arch do `sudo pacman -Rns libreoffice-fresh`

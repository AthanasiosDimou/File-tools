import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from pypdf import PdfReader, PdfWriter

# --- Shared Logic ---

def remove_restrictions(input_path: str, output_path: str, password: str = None) -> tuple[bool, str | None]:
    """
    Reads a PDF and writes it to a new file, removing restrictions.
    """
    try:
        reader = PdfReader(input_path)
        writer = PdfWriter()

        if reader.is_encrypted:
            if password:
                reader.decrypt(password)
            else:
                try:
                    # Try blank password for simple ownership restrictions
                    reader.decrypt("")
                except Exception:
                    pass 

        for page in reader.pages:
            writer.add_page(page)

        with open(output_path, "wb") as output_file:
            writer.write(output_file)
        
        return True, None
    except Exception as e:
        return False, str(e)

# --- GUI Application ---

class PdfToolApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Fixer & Unlocker")
        self.root.geometry("600x500")
        
        # --- Options Section ---
        options_frame = tk.LabelFrame(root, text="Operation Mode", padx=10, pady=10)
        options_frame.pack(fill="x", padx=10, pady=5)
        
        self.mode_var = tk.StringVar(value="fix")
        
        rb1 = tk.Radiobutton(options_frame, text="Repair / Fix Corruption (Re-save file)", 
                             variable=self.mode_var, value="fix", command=self.toggle_password)
        rb1.pack(anchor="w")
        
        rb2 = tk.Radiobutton(options_frame, text="Unprotect / Remove Password", 
                             variable=self.mode_var, value="unlock", command=self.toggle_password)
        rb2.pack(anchor="w")
        
        # --- Password Section ---
        pass_frame = tk.Frame(root)
        pass_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(pass_frame, text="Password (for Unprotect mode):").pack(side="left")
        self.pass_entry = tk.Entry(pass_frame, show="*", width=30)
        self.pass_entry.pack(side="left", padx=5)
        self.pass_entry.config(state="disabled") # Disabled by default
        
        # --- Action Buttons ---
        btn_frame = tk.Frame(root, pady=10)
        btn_frame.pack(fill="x", padx=10)
        
        tk.Button(btn_frame, text="Process Single File", command=self.process_file, bg="#dddddd", height=2).pack(side="left", expand=True, fill="x", padx=2)
        tk.Button(btn_frame, text="Process Batch Folder", command=self.process_folder, bg="#dddddd", height=2).pack(side="left", expand=True, fill="x", padx=2)

        # --- Log Area ---
        self.log_area = scrolledtext.ScrolledText(root, height=15)
        self.log_area.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.log("Welcome! Select a mode and choose a file or folder.")

    def toggle_password(self):
        if self.mode_var.get() == "unlock":
            self.pass_entry.config(state="normal")
        else:
            self.pass_entry.config(state="disabled")

    def log(self, message):
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)
        self.root.update()

    def get_output_path(self, input_path):
        folder, filename = os.path.split(input_path)
        prefix = "fixed_" if self.mode_var.get() == "fix" else "unprotected_"
        
        # Avoid double prefixes
        if filename.startswith("fixed_") or filename.startswith("unprotected_"):
            return None
            
        return os.path.join(folder, f"{prefix}{filename}")

    def process_file(self):
        in_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if not in_path:
            return
            
        out_path = self.get_output_path(in_path)
        password = self.pass_entry.get() if self.mode_var.get() == "unlock" else None
        
        self.log(f"Processing: {in_path}...")
        
        success, err = remove_restrictions(in_path, out_path, password)
        if success:
            self.log(f"SUCCESS -> Saved to: {out_path}")
            messagebox.showinfo("Done", "File processed successfully!")
        else:
            self.log(f"ERROR -> {err}")
            messagebox.showerror("Error", f"Failed to process file:\n{err}")

    def process_folder(self):
        in_dir = filedialog.askdirectory()
        if not in_dir:
            return
            
        password = self.pass_entry.get() if self.mode_var.get() == "unlock" else None
        
        self.log(f"Scanning folder: {in_dir}...")
        files = [f for f in os.listdir(in_dir) if f.lower().endswith('.pdf')]
        
        if not files:
            self.log("No partial PDF files found.")
            return

        count = 0
        errors = 0
        
        for filename in files:
            in_path = os.path.join(in_dir, filename)
            out_path = self.get_output_path(in_path)
            
            # Skip files we already created or invalid paths
            if not out_path: 
                continue
            
            success, err = remove_restrictions(in_path, out_path, password)
            if success:
                self.log(f"Fixed: {filename}")
                count += 1
            else:
                self.log(f"Failed: {filename} ({err})")
                errors += 1
        
        self.log(f"--- Batch Complete ---")
        self.log(f"Successful: {count}")
        self.log(f"Errors: {errors}")
        messagebox.showinfo("Batch Complete", f"Processed {count} files.\n{errors} errors.")

if __name__ == "__main__":
    root = tk.Tk()
    app = PdfToolApp(root)
    root.mainloop()
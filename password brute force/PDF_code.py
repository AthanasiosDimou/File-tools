import os
import tkinter as tk
from tkinter import filedialog
import pikepdf
# Import everything from your password generator
from passwordGenerator import *

def select_pdf_file():
    """Opens a file manager to select the PDF."""
    root = tk.Tk()
    root.withdraw()  # Hide the main tkinter window
    file_path = filedialog.askopenfilename(
        title="Select the encrypted PDF",
        filetypes=[("PDF files", "*.pdf")]
    )
    return file_path

def try_password(pdf_path, password):
    """Attempts to open the PDF with the given password."""
    try:
        with pikepdf.open(pdf_path, password=password) as pdf:
            return True 
    except (pikepdf.PasswordError, pikepdf.EncryptionError):
        return False

if __name__ == "__main__":
    # 1. Get the file path using GUI
    pdf_path = select_pdf_file()
    
    if not pdf_path:
        print("No file selected. Exiting.")
        sys.exit()

    print(f"Targeting: {pdf_path}")

    # 2. Setup (from your passwordGenerator)
    # The 'ASCII' list and 'password_max' are initialized in passwordGenerator.py
    # when it was imported. We just need to start the loop.
    
    counter = 0
    while True:
        generate()
        counter += 1
        guess = convert()
        
        # Testing the guess
        if try_password(pdf_path, guess):
            print("\n" + "---- FOUND ----")
            print(f"Password = {guess}")
            print(f"Attempts = {counter}")
            
            # Save the result
            with open("found_password.txt", "w") as f:
                f.write(guess)
            break
        
        if counter % 100 == 0:
            print(f"Trying: {guess} ({counter} attempts)")
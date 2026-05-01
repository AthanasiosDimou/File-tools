import tkinter as tk
from tkinter import filedialog
import pikepdf
import io

from typing import List

import passwordGenerator as pg # Import as a module


def select_pdf_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(title="Select the encrypted PDF")
    return file_path

def test_passwords_txt(passwords: List[str], pdf_bytes: bytes):
    for password in passwords:
        try:
            with pikepdf.open(io.BytesIO(pdf_bytes), password=password) as pdf:
                print(f"Password found: {password}")
                return password
        except pikepdf.PasswordError:
            continue
    return None


if __name__ == "__main__":
    
    # Define these at the module level so they are accessible after import
    ascii_min: int = 32
    ascii_max: int = 126

    # If your generator needs to know the password length to brute force:
    # Set the variables inside the imported module

    password_max: int = 10 # Change this to the length you are testing
    ASCII: list[int] = [ascii_min - 1] * password_max # Pre-fill the list

    log_file: str = "passwords.txt"

    # Get the file path via GUI
    pdf_path: str = select_pdf_file()
    if not pdf_path:
        print("No file selected.")
        exit()

    print(f"Loading PDF into memory: {pdf_path}")
    # Read PDF into memory to avoid disk I/O on every password guess
    with open(pdf_path, 'rb') as f:
        pdf_bytes = f.read()

    # Try passwords from file first
    try:
        with open(log_file, "r") as f:
            passwords = [line.strip().split(" | ")[0].replace("Password found: ", "") for line in f if "Password found: " in line]
            # Also just try raw passwords if they are in the file
            f.seek(0)
            passwords.extend([line.strip() for line in f if " | " not in line])
            
        found_pass = test_passwords_txt(passwords, pdf_bytes)
        if found_pass:
            print("Password found in log file!")
            exit()
    except FileNotFoundError:
        pass

    print(f"Brute forcing: {pdf_path}")
    
    counter: int = 0
    while True:
        pg.generate(ASCII, password_max, ascii_min, ascii_max)
        counter += 1
        guess: str = pg.convert(ASCII, password_max, ascii_min)
        
        try:
            with pikepdf.open(io.BytesIO(pdf_bytes), password=guess) as pdf:
                result_text: str = f"Password found: {guess} | Attempts: {counter}"
                print(f"\n---- FOUND ----\n{result_text}")
                
                # Append to the text file
                with open(log_file, "a") as f:
                    f.write(result_text + "\n")
                break

        except:
            if counter % 10000 == 0: # print attempt every 10000 tries to avoid flooding the console
              print(f"Attempts: {counter} | Last guess: {guess}")

# python's prints are  quite slow on the CPU so we will lessen the amount of prints to speed up the brute force process.
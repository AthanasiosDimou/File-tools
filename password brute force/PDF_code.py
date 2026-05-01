import tkinter as tk
from tkinter import filedialog
import pikepdf
import concurrent.futures
import multiprocessing
import time
import io

from typing import List

import passwordGenerator as pg # Import as a module


def select_pdf_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(title="Select the encrypted PDF")
    return file_path

def test_passwords_txt(passwords: List[str], pdf_data: bytes):
    for password in passwords:
        try:
            with pikepdf.open(io.BytesIO(pdf_data), password=password) as pdf:
                print(f"Password found: {password}")
                return password
        except pikepdf.PasswordError:
            continue
        except Exception:
            # Handle other possible pikepdf exceptions silently
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
        
    print(f"Loading {pdf_path} into memory...")
    with open(pdf_path, "rb") as f:
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
    
    BATCH_SIZE: int = 5000
    max_workers: int = multiprocessing.cpu_count()
    
    counter: int = 0
    start_time = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        active_futures = set()
        found_password = None
        
        while found_password is None:
            # Maintain a queue of tasks
            while len(active_futures) < max_workers * 2:
                batch = []
                for _ in range(BATCH_SIZE):
                    pg.generate(ASCII, password_max, ascii_min, ascii_max)
                    guess = pg.convert(ASCII, password_max, ascii_min)
                    batch.append(guess)
                
                counter += BATCH_SIZE
                active_futures.add(executor.submit(test_passwords_txt, batch, pdf_bytes))

            # Wait for completed tasks
            done, active_futures = concurrent.futures.wait(
                active_futures, 
                return_when=concurrent.futures.FIRST_COMPLETED
            )
            
            for future in done:
                res = future.result()
                if res:
                    found_password = res
                    break

            if counter % 50000 == 0 or (counter - BATCH_SIZE) % 50000 <= BATCH_SIZE: 
                print(f"Attempts: ~{counter} | Time elapsed: {time.time() - start_time:.2f}s")
        
        if found_password:
            result_text: str = f"Password found: {found_password} | Total Batched Attempts: ~{counter}"
            print(f"\n---- FOUND ----\n{result_text}")
            
            # Append to the text file
            with open(log_file, "a") as f:
                f.write(result_text + "\n")

# Using multithreading and batching significantly speeds up the process on free-threaded 3.14 (and even in older versions since qpdf releases the GIL).
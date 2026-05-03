import argparse
import tkinter as tk
from tkinter import filedialog
import pikepdf
import concurrent.futures
import multiprocessing
import time
import io
import sys

from typing import List

import passwordGenerator as pg # Import as a module


def select_pdf_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(title="Select the encrypted PDF")
    return file_path

def test_passwords_txt(passwords: List[str], pdf_path: str):
    for password in passwords:
        try:
            with pikepdf.open(pdf_path, password=password) as pdf:
                return password
        except pikepdf.PasswordError:
            continue
        except Exception:
            # Handle other possible pikepdf exceptions silently
            continue
    return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PDF Password Brute Forcer")
    parser.add_argument("--single-thread", action="store_true", help="Run in single-threaded mode (default is multi-processing based on CPU count)")
    parser.add_argument("--min-len", type=int, default=1, help="Minimum password length")
    parser.add_argument("--max-len", type=int, default=10, help="Maximum password length")
    args = parser.parse_args()

    # Define these at the module level so they are accessible after import
    ascii_min: int = 48 # original 32
    ascii_max: int = 122 # original 126

    log_file: str = "passwords.txt"

    # Get the file path via GUI
    pdf_path: str = select_pdf_file()
    if not pdf_path:
        print("No file selected.")
        exit()

    # Try passwords from file first
    try:
        with open(log_file, "r") as f:
            passwords = [line.strip().split(" | ")[0].replace("Password found: ", "") for line in f if "Password found: " in line]
            f.seek(0)
            passwords.extend([line.strip() for line in f if " | " not in line])
            
        found_pass = test_passwords_txt(passwords, pdf_path)
        if found_pass:
            print("Password found in log file!")
            print(f"Password: {found_pass}")
            exit()
    except FileNotFoundError:
        pass

    BATCH_SIZE: int = 5000 if not args.single_thread else 1000
    max_workers: int = 1 if args.single_thread else multiprocessing.cpu_count()
    
    counter: int = 0
    start_time = time.time()
    
    found_password = None

    for current_len in range(args.min_len, args.max_len + 1):
        if found_password:
            break
        
        # We prepare ASCII to just represent the current_len.
        # However, to avoid pg.sys.exit() from generate() ending this script 
        # when it finishes the length, we could either patch pg in memory, or 
        # just know that `pg.generate` relies on array sizes.
        # Wait, if we use pg.generate, it will sys.exit() on completion.
        # Instead, we can manually implement the iteration loop or monkey-patch sys.exit?
        # A simpler way without rewriting generate() is to use `pg.increase` and `pg.extend` directly here.
        
        ASCII: list[int] = [ascii_min] * current_len
        
        # Function to generate next password, avoiding pg.generate's sys.exit()
        def get_next_guess():
            global current_len, ASCII
            for i in range(current_len - 1, -1, -1):
                if pg.increase(i, ASCII, ascii_min, ascii_max, current_len):
                    return pg.convert(ASCII, current_len, ascii_min)
            return None
        
        guess = pg.convert(ASCII, current_len, ascii_min) # Initial
        total_generated = 1

        if not args.single_thread:
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                active_futures = set()
                
                while guess is not None and found_password is None:
                    # Maintain a queue of tasks
                    while len(active_futures) < max_workers * 2 and guess is not None:
                        batch = []
                        for _ in range(BATCH_SIZE):
                            if guess is not None:
                                batch.append(guess)
                                guess = get_next_guess()
                            else:
                                break
                        
                        counter += len(batch)
                        total_generated += len(batch)
                        active_futures.add(executor.submit(test_passwords_txt, batch, pdf_path))

                    # Wait for completed tasks
                    if active_futures:
                        done, active_futures = concurrent.futures.wait(
                            active_futures, 
                            return_when=concurrent.futures.FIRST_COMPLETED
                        )
                        
                        for future in done:
                            res = future.result()
                            if res:
                                found_password = res
                                break
        else:
            # Single threaded
            batch = []
            while guess is not None and found_password is None:
                batch.append(guess)
                guess = get_next_guess()

                if len(batch) >= BATCH_SIZE or guess is None:
                    counter += len(batch)
                    res = test_passwords_txt(batch, pdf_path)
                    if res:
                        found_password = res
                        break
                    batch = []
        
    if found_password:
        result_text: str = f"Password found: {found_password} | Total Batched Attempts: ~{counter}"
        print(f"\n---- FOUND ----\n{result_text}")
        
        # Append to the text file
        with open(log_file, "a") as f:
            f.write(result_text + "\n")

# Using multithreading and batching significantly speeds up the process on free-threaded 3.14 (and even in older versions since qpdf releases the GIL).
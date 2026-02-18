import curses
import os
import sys
import time
from PyPDF2 import PdfReader, PdfWriter

# --- Shared Logic ---

def remove_restrictions(input_path, output_path, password=None):
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
                except:
                    pass 

        for page in reader.pages:
            writer.add_page(page)

        with open(output_path, "wb") as output_file:
            writer.write(output_file)
        
        return True, None
    except Exception as e:
        return False, str(e)

# --- UI Helpers ---

def draw_menu(stdscr, selected_row_idx, options):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    
    title = "PDF SECURITY REMOVER & FIXER"
    stdscr.addstr(1, w//2 - len(title)//2, title, curses.A_BOLD)
    
    subtitle = "Select an option using UP/DOWN arrows and ENTER"
    stdscr.addstr(2, w//2 - len(subtitle)//2, subtitle, curses.A_DIM)

    for idx, row in enumerate(options):
        x = w//2 - len(row)//2
        y = h//2 - len(options)//2 + idx
        if idx == selected_row_idx:
            stdscr.attron(curses.color_pair(1))
            stdscr.addstr(y, x, row)
            stdscr.attroff(curses.color_pair(1))
        else:
            stdscr.addstr(y, x, row)

    stdscr.refresh()

def get_user_input(stdscr, prompt):
    """
    Custom input handler to keep the screen clean and handle basic backspacing.
    """
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    stdscr.addstr(h//2 - 2, 2, prompt, curses.A_BOLD)
    stdscr.addstr(h//2, 2, "> ")
    curses.echo()
    curses.curs_set(1)
    
    # Get string
    input_bytes = stdscr.getstr(h//2, 4)
    user_input = input_bytes.decode('utf-8').strip()
    
    # Remove quotes if user dragged-and-dropped file into terminal
    user_input = user_input.replace('"', '').replace("'", "")
    
    curses.noecho()
    curses.curs_set(0)
    return user_input

def show_status(stdscr, messages):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    
    # Print messages (handling overflow simply by cutting off for now)
    start_y = 1
    for msg in messages:
        if start_y < h - 2:
            stdscr.addstr(start_y, 2, msg[:w-3])
            start_y += 1
    
    stdscr.addstr(h-2, 2, "Press any key to return to menu...", curses.A_BLINK)
    stdscr.refresh()
    stdscr.getch()

# --- Main Application Logic ---

def main(stdscr):
    # Setup colors
    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE) # Highlight
    curses.curs_set(0) # Hide cursor

    options = [
        "1. Repair Corrupt PDF (Single File)",
        "2. Repair Corrupt PDFs (Batch Folder)",
        "3. Unprotect PDF with Password (Single File)",
        "4. Unprotect PDFs with Password (Batch Folder)",
        "5. Exit"
    ]
    
    current_row = 0

    while True:
        draw_menu(stdscr, current_row, options)
        key = stdscr.getch()

        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(options) - 1:
            current_row += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            
            # EXIT
            if current_row == 4:
                break
            
            # Get Password if needed (Options 3 & 4)
            pdf_password = None
            if current_row in [2, 3]:
                pdf_password = get_user_input(stdscr, "Enter PDF Password:")

            # LOGIC FOR OPTION 1 & 3 (SINGLE FILES)
            if current_row == 0 or current_row == 2:
                in_path = get_user_input(stdscr, "Enter path to INPUT PDF file:")
                
                if not os.path.isfile(in_path):
                    show_status(stdscr, [f"Error: File not found: {in_path}"])
                    continue

                folder, filename = os.path.split(in_path)
                prefix = "fixed_" if current_row == 0 else "unprotected_"
                out_path = os.path.join(folder, f"{prefix}{filename}")

                stdscr.clear()
                stdscr.addstr(0, 0, "Processing...")
                stdscr.refresh()
                
                success, err = remove_restrictions(in_path, out_path, pdf_password)
                
                if success:
                    show_status(stdscr, [f"Success! Saved to:", f"{out_path}"])
                else:
                    show_status(stdscr, [f"Failed to process file.", f"Error: {err}"])

            # LOGIC FOR OPTION 2 & 4 (BATCH FOLDERS)
            elif current_row == 1 or current_row == 3:
                in_dir = get_user_input(stdscr, "Enter path to INPUT FOLDER:")
                
                if not os.path.isdir(in_dir):
                    show_status(stdscr, [f"Error: Directory not found: {in_dir}"])
                    continue

                # Auto output to same folder for simplicity
                out_dir = in_dir

                # Process files
                stdscr.clear()
                stdscr.addstr(0, 0, "Processing batch... please wait.")
                stdscr.refresh()
                
                log = []
                count = 0
                
                files = [f for f in os.listdir(in_dir) if f.lower().endswith('.pdf')]
                
                if not files:
                    show_status(stdscr, ["No PDF files found in that directory."])
                    continue

                for filename in files:
                    # Avoid loops
                    if filename.startswith("fixed_") or filename.startswith("unprotected_"):
                        continue
                        
                    in_path = os.path.join(in_dir, filename)
                    
                    prefix = "fixed_" if current_row == 1 else "unprotected_"
                    out_path = os.path.join(out_dir, f"{prefix}{filename}")
                    
                    success, err = remove_restrictions(in_path, out_path, pdf_password)
                    if success:
                        count += 1
                        stdscr.addstr(2, 0, f"Processed: {filename}" + " "*20) 
                        stdscr.refresh()
                    else:
                        log.append(f"Failed: {filename} ({err})")
                
                log.insert(0, f"Batch complete. Processed {count} files.")
                show_status(stdscr, log)

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        if os.name == 'nt':
            print("Tip: If you are on Windows, ensure you simply run: pip install windows-curses")
        
        print("\nPress Enter to exit...")
        input()
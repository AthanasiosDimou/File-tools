# PDF Password Brute Forcer

Efficiently crack PDF passwords using optimized brute force with in-memory batching.

## How It Works

1. **Reads PDF into Memory** - Loads entire PDF once to avoid repeated disk I/O
2. **Generates Passwords** - Systematically generates all combinations
3. **Batch Testing** - Tests multiple passwords per attempt (in-memory)
4. **Multithreading** - Uses all available CPU cores for parallel testing
5. **Thread Pool** - Maintains queue of pending tasks for optimal throughput

## Features

- **Smart Batching** - Tests passwords in batches to reduce overhead
- **In-Memory PDF** - PDF stays in RAM throughout cracking process
- **Multi-core Optimized** - Automatic CPU count detection
- **Dictionary Support** - Tests common passwords first before brute force
- **Progress Tracking** - Shows attempt count and current guess on interrupt

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
python PDF_code.py
```

Opens a file dialog to select the PDF file. Then:
- Checks `passwords.txt` for previously found passwords
- Attempts brute force starting from length 1 to 10
- Tries all ASCII printable characters (digits, letters, symbols)

### With Custom Length Range

```bash
python PDF_code.py --min-len 4 --max-len 8
```

Brute force passwords between 4 and 8 characters.

### Single-threaded Mode

```bash
python PDF_code.py --single-thread
```

Useful for debugging or systems with few cores.

## Performance Optimization

The key optimization is **in-memory batching**:

```
OLD (Slow):
PDF File → pikepdf.open() → test password 1
PDF File → pikepdf.open() → test password 2
PDF File → pikepdf.open() → test password 3
[Repeated disk reads and PDF parsing]

NEW (Fast):
PDF File → (read once) → Memory (5000 copies in workers)
  ├─ Worker 1: test passwords 1-5000
  ├─ Worker 2: test passwords 5001-10000
  ├─ Worker 3: test passwords 10001-15000
  └─ Worker 4: test passwords 15001-20000
[No repeated disk I/O]
```

## Configuration

Edit `PDF_code.py` to adjust:

```python
BATCH_SIZE = 5000  # Passwords per batch (default)
# Adjust based on:
#   - Higher = fewer threads woken, but more memory
#   - Lower = more thread overhead, but lower memory

max_workers = multiprocessing.cpu_count()  # Number of parallel workers
# Adjust based on:
#   - More = better CPU utilization
#   - Fewer = less memory usage
```

## Dictionary Attack

Place common passwords in `passwords.txt` with format:

```
password1
password2
password3
Password found: previouslyCracked | Total Batched Attempts: 50000
```

The script will:
1. Check for "Password found:" entries (successful cracks)
2. Test other lines as potential passwords
3. Fall back to brute force if not found

## Files

- `PDF_code.py` - Main PDF password cracker
- `passwordGenerator.py` - Password generation utility
- `passwords.txt` - Log of found passwords and dictionary
- `requirements.txt` - Dependencies (pikepdf)

## Example Session

```
$ python PDF_code.py
[File dialog opens - select PDF]
Testing dictionary passwords...
Attempting brute force (length 1-10)...
---- FOUND ----
Password found: myPassword123 | Total Batched Attempts: ~125000
```

The password will be logged to `passwords.txt` for future use.

## Troubleshooting

### Very Slow Performance

- Reduce `--max-len` to search shorter passwords first
- Use `--dict` with common passwords before brute force
- Remove unnecessary programs to free RAM

### Out of Memory

- Reduce `BATCH_SIZE` in `PDF_code.py`
- Use `--single-thread` mode
- Reduce `max_workers` manually

### No Password Found

- Try increasing `--max-len`
- Try a different character set in `passwordGenerator.py`
- PDF might use unsupported encryption (AES-256, public key)

## Limitations

- **PDF Encryption Only** - Works only on password-protected PDFs
- **AES-256** - May not work with newer AES-256 encryption
- **Brute Force Time** - Exponential growth: 95^8 ≈ 6.6 quadrillion possibilities
- **No Wordlist Attack** - Only dictionary + systematic brute force

## Ethical Use

This tool is for:
- ✅ Recovering your own forgotten PDF passwords
- ✅ Testing PDF security
- ✅ Educational purposes

This tool is NOT for:
- ❌ Cracking PDFs without permission
- ❌ Unauthorized access
- ❌ Illegal activities

Use responsibly and legally.

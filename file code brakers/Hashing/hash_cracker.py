"""
Hash Cracker - Brute Force Common Encryption Hashes
Similar to PDF_code.py but for password hashes

Supports:
- MD5
- SHA-1
- SHA-256
- bcrypt (slower, but more secure)
- PDF hashes (extracted via pdf2john.py)

Uses batching and multithreading for efficiency
"""

import argparse
import hashlib
import time
import concurrent.futures
import multiprocessing
import io
import sys
from typing import List, Optional, Tuple
from pathlib import Path

try:
    import bcrypt
    BCRYPT_AVAILABLE = True
except ImportError:
    BCRYPT_AVAILABLE = False

import file_code_brakers.Hashing.passwordGenerator as pg


def compute_hash(password: str, hash_type: str) -> str:
    """
    Compute hash of a password.
    
    Args:
        password: Password to hash
        hash_type: Type of hash ('md5', 'sha1', 'sha256')
    
    Returns:
        Hex digest of the hash
    """
    if hash_type.lower() == 'md5':
        return hashlib.md5(password.encode()).hexdigest()
    elif hash_type.lower() == 'sha1':
        return hashlib.sha1(password.encode()).hexdigest()
    elif hash_type.lower() == 'sha256':
        return hashlib.sha256(password.encode()).hexdigest()
    else:
        raise ValueError(f"Unsupported hash type: {hash_type}")


def check_bcrypt(password: str, hash_digest: bytes) -> bool:
    """Check if password matches bcrypt hash."""
    if not BCRYPT_AVAILABLE:
        return False
    try:
        return bcrypt.checkpw(password.encode(), hash_digest)
    except Exception:
        return False


def test_passwords_batch(passwords: List[str], target_hash: str, hash_type: str) -> Optional[str]:
    """
    Test a batch of passwords against target hash.
    
    Args:
        passwords: List of passwords to try
        target_hash: The hash we're trying to crack
        hash_type: Type of hash ('md5', 'sha1', 'sha256', 'bcrypt')
    
    Returns:
        Matching password if found, None otherwise
    """
    target_hash_lower = target_hash.lower()
    
    for password in passwords:
        try:
            if hash_type.lower() == 'bcrypt':
                if check_bcrypt(password, target_hash.encode()):
                    return password
            else:
                computed = compute_hash(password, hash_type)
                if computed == target_hash_lower:
                    return password
        except Exception:
            continue
    
    return None


def load_dictionary(filepath: str) -> List[str]:
    """Load passwords from a dictionary file."""
    try:
        with open(filepath, 'r', errors='ignore') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Dictionary file not found: {filepath}")
        return []


def crack_hash(target_hash: str, hash_type: str = 'md5', 
               dictionary: Optional[str] = None, 
               min_len: int = 1, max_len: int = 8,
               single_thread: bool = False) -> Tuple[Optional[str], int, float]:
    """
    Crack a hash using dictionary attack or brute force.
    
    Args:
        target_hash: Hash to crack
        hash_type: Type of hash
        dictionary: Path to dictionary file (None for brute force)
        min_len: Minimum password length
        max_len: Maximum password length
        single_thread: Use single thread if True
    
    Returns:
        Tuple of (password, attempts, time_elapsed)
    """
    start_time = time.time()
    counter = 0
    found_password = None
    last_guess = None
    
    BATCH_SIZE = 5000 if not single_thread else 1000
    max_workers = 1 if single_thread else multiprocessing.cpu_count()
    
    # Try dictionary attack first
    if dictionary:
        print(f"Attempting dictionary attack from: {dictionary}")
        passwords = load_dictionary(dictionary)
        
        if not single_thread:
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                active_futures = set()
                
                for i in range(0, len(passwords), BATCH_SIZE):
                    batch = passwords[i:i + BATCH_SIZE]
                    counter += len(batch)
                    
                    future = executor.submit(test_passwords_batch, batch, target_hash, hash_type)
                    active_futures.add(future)
                    
                    if len(active_futures) >= max_workers * 2:
                        done, active_futures = concurrent.futures.wait(
                            active_futures,
                            return_when=concurrent.futures.FIRST_COMPLETED
                        )
                        
                        for f in done:
                            res = f.result()
                            if res:
                                found_password = res
                                break
                        
                        if found_password:
                            break
        else:
            # Single threaded dictionary
            batch = []
            for password in passwords:
                batch.append(password)
                if len(batch) >= BATCH_SIZE:
                    res = test_passwords_batch(batch, target_hash, hash_type)
                    if res:
                        found_password = res
                        break
                    batch = []
        
        if found_password:
            elapsed = time.time() - start_time
            return (found_password, counter, elapsed)
    
    # Brute force if dictionary didn't work or wasn't provided
    print(f"Attempting brute force (length {min_len}-{max_len})...")
    ascii_min, ascii_max = 48, 122  # ASCII characters
    
    try:
        for current_len in range(min_len, max_len + 1):
            if found_password:
                break
            
            ASCII = [ascii_min] * current_len
            
            def get_next_guess():
                nonlocal ASCII
                for i in range(current_len - 1, -1, -1):
                    if pg.increase(i, ASCII, ascii_min, ascii_max, current_len):
                        return pg.convert(ASCII, current_len, ascii_min)
                return None
            
            guess = pg.convert(ASCII, current_len, ascii_min)
            
            if not single_thread:
                with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                    active_futures = set()
                    
                    while guess is not None and found_password is None:
                        while len(active_futures) < max_workers * 2 and guess is not None:
                            batch = []
                            for _ in range(BATCH_SIZE):
                                if guess is not None:
                                    batch.append(guess)
                                    last_guess = guess
                                    guess = get_next_guess()
                                else:
                                    break
                            
                            counter += len(batch)
                            active_futures.add(
                                executor.submit(test_passwords_batch, batch, target_hash, hash_type)
                            )
                        
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
                # Single threaded brute force
                batch = []
                while guess is not None and found_password is None:
                    batch.append(guess)
                    last_guess = guess
                    guess = get_next_guess()
                    
                    if len(batch) >= BATCH_SIZE or guess is None:
                        counter += len(batch)
                        res = test_passwords_batch(batch, target_hash, hash_type)
                        if res:
                            found_password = res
                            break
                        batch = []
    
    except KeyboardInterrupt:
        elapsed = time.time() - start_time
        print(f"\n\n---- INTERRUPTED ----")
        print(f"Attempts made: ~{counter}")
        print(f"Last attempt: {last_guess}")
        print(f"Time elapsed: {elapsed:.2f}s")
        sys.exit()
    
    elapsed = time.time() - start_time
    return (found_password, counter, elapsed)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Hash Cracker - Brute Force Common Encryption Hashes"
    )
    parser.add_argument("hash", help="Hash to crack")
    parser.add_argument(
        "--type", 
        choices=['md5', 'sha1', 'sha256', 'bcrypt'],
        default='md5',
        help="Hash type (default: md5)"
    )
    parser.add_argument(
        "--dict",
        help="Dictionary file for dictionary attack"
    )
    parser.add_argument(
        "--min-len", 
        type=int, 
        default=1, 
        help="Minimum password length for brute force"
    )
    parser.add_argument(
        "--max-len", 
        type=int, 
        default=8, 
        help="Maximum password length for brute force"
    )
    parser.add_argument(
        "--single-thread", 
        action="store_true", 
        help="Use single-threaded mode"
    )
    
    args = parser.parse_args()
    
    print(f"Hash Cracker")
    print(f"Target hash: {args.hash}")
    print(f"Hash type: {args.type}")
    print()
    
    password, attempts, elapsed = crack_hash(
        target_hash=args.hash,
        hash_type=args.type,
        dictionary=args.dict,
        min_len=args.min_len,
        max_len=args.max_len,
        single_thread=args.single_thread
    )
    
    if password:
        result = f"Password found: {password} | Type: {args.type} | Attempts: ~{attempts} | Time: {elapsed:.2f}s"
        print(f"\n---- FOUND ----\n{result}\n")
        
        # Log result
        with open("cracked_hashes.txt", "a") as f:
            f.write(result + "\n")
    else:
        print(f"\n---- NOT FOUND ----")
        print(f"Attempts: ~{attempts}")
        print(f"Time elapsed: {elapsed:.2f}s")
